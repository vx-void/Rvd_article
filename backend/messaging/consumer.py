import pika
import json
import os
import logging
import time
import signal
import sys
from typing import Optional, Dict, Any, Callable
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class RMQConsumer:
    """Потребитель сообщений из RabbitMQ"""

    def __init__(
            self,
            host: Optional[str] = None,
            port: Optional[int] = None,
            queue_name: str = 'search_queue',
            worker_factory: Optional[Callable] = None,
            prefetch_count: int = 1,
            heartbeat: int = 600,
            recreate_queue: bool = False
    ):
        """
        Инициализация потребителя RabbitMQ.

        Args:
            host: Хост RabbitMQ (по умолчанию из env RABBITMQ_HOST или localhost)
            port: Порт RabbitMQ (по умолчанию из env RABBITMQ_PORT или 5672)
            queue_name: Имя очереди для потребления
            worker_factory: Фабрика для создания worker'ов
            prefetch_count: Количество сообщений для предварительной выборки
            heartbeat: Таймаут heartbeat в секундах
            recreate_queue: Пересоздать очередь при конфликте параметров
        """
        self.host = host or os.getenv("RABBITMQ_HOST", "localhost")
        self.port = port or int(os.getenv("RABBITMQ_PORT", 5672))
        self.queue_name = queue_name
        self.worker_factory = worker_factory
        self.prefetch_count = prefetch_count
        self.heartbeat = heartbeat
        self.recreate_queue = recreate_queue

        # Состояние подключения
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
        self.is_consuming = False
        self.should_reconnect = True
        self.consumer_tag: Optional[str] = None

        # Настройка обработчиков сигналов
        self._setup_signal_handlers()

        # Первоначальное подключение
        self._connect()

    def _setup_signal_handlers(self):
        """Настройка обработчиков сигналов для graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        logger.info(f"Получен сигнал {signum}, выполняется graceful shutdown...")
        self.should_reconnect = False
        self.stop()

    @contextmanager
    def _logging_context(self, task_id: str = "unknown"):
        """
        Контекстный менеджер для логирования с task_id.

        Args:
            task_id: Идентификатор задачи для логирования
        """
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.task_id = task_id
            return record

        logging.setLogRecordFactory(record_factory)
        try:
            yield
        finally:
            logging.setLogRecordFactory(old_factory)

    def _connect(self):
        """Установка соединения с RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    heartbeat=self.heartbeat,
                    connection_attempts=3,
                    retry_delay=5,
                    blocked_connection_timeout=300
                )
            )
            self.channel = self.connection.channel()

            # Пробуем объявить очередь
            try:
                if self.recreate_queue:
                    # Пытаемся удалить старую очередь
                    try:
                        self.channel.queue_delete(self.queue_name)
                        logger.info(f"Очередь {self.queue_name} удалена для пересоздания")
                    except:
                        pass

                # Объявляем очередь
                self.channel.queue_declare(
                    queue=self.queue_name,
                    durable=True
                )

                logger.info(f"Подключено к RabbitMQ {self.host}:{self.port}")
                return

            except pika.exceptions.ChannelClosedByBroker as e:
                if "PRECONDITION_FAILED" in str(e):
                    logger.warning(f"Очередь {self.queue_name} уже существует с другими параметрами")
                    # Пробуем использовать пассивное объявление
                    self.channel = self.connection.channel()
                    self.channel.queue_declare(
                        queue=self.queue_name,
                        durable=True,
                        passive=True  # Только проверяем существование
                    )
                    logger.info(f"Используем существующую очередь {self.queue_name}")
                    return
                else:
                    raise

        except Exception as e:
            logger.error(f"Неожиданная ошибка подключения: {e}")
            raise

    def _reconnect(self):
        """Повторное подключение при обрыве соединения"""
        if not self.should_reconnect:
            return False

        logger.info("Попытка переподключения к RabbitMQ...")
        try:
            # Закрываем старые соединения если они есть
            if self.connection and not self.connection.is_closed:
                try:
                    self.connection.close()
                except:
                    pass

            self._connect()
            logger.info("Переподключение успешно")
            return True
        except Exception as e:
            logger.error(f"Ошибка переподключения: {e}")
            return False

    def _validate_message(self, message: Dict[str, Any]) -> Optional[str]:
        """
        Валидация входящего сообщения.

        Args:
            message: Сообщение для валидации

        Returns:
            Optional[str]: Сообщение об ошибке или None если валидация успешна
        """
        if not isinstance(message, dict):
            return "Сообщение должно быть словарем"

        required_fields = ['task_id', 'query']
        for field in required_fields:
            if field not in message:
                return f"Отсутствует обязательное поле: {field}"

        if not isinstance(message['task_id'], str):
            return "task_id должен быть строкой"

        if not isinstance(message['query'], str):
            return "query должен быть строкой"

        if not message['query'].strip():
            return "query не может быть пустым"

        return None

    def _create_worker(self):
        """Создание worker'а с правильным импортом"""
        try:
            if self.worker_factory:
                return self.worker_factory()

            # Пробуем несколько способов импорта
            try:
                # Способ 1: Абсолютный импорт
                from backend.messaging.worker import RMQWorker
                return RMQWorker()
            except ImportError:
                try:
                    # Способ 2: Относительный импорт (если файл запускается как модуль)
                    from .worker import RMQWorker
                    return RMQWorker()
                except ImportError:
                    try:
                        # Способ 3: Прямой импорт из файла
                        import sys
                        import os
                        # Добавляем путь к проекту
                        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                        if project_root not in sys.path:
                            sys.path.append(project_root)

                        from backend.messaging.worker import RMQWorker
                        return RMQWorker()
                    except ImportError as e:
                        logger.error(f"Не удалось импортировать worker: {e}")
                        raise

        except Exception as e:
            logger.error(f"Ошибка создания worker: {e}")
            raise

    def _callback(self, ch, method, properties, body):
        """Callback функция для обработки сообщений из очереди"""
        task_id = "unknown"

        try:
            # Декодирование сообщения
            if not body:
                logger.error("Получено пустое сообщение")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return

            message = json.loads(body)
            task_id = message.get('task_id', 'unknown')

            # Используем контекст для логирования
            with self._logging_context(task_id):
                logger.info(f"Начало обработки задачи")

                # Валидация сообщения
                validation_error = self._validate_message(message)
                if validation_error:
                    logger.error(f"Ошибка валидации сообщения: {validation_error}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    return

                # Получаем количество попыток обработки из headers
                retry_count = 0
                if properties.headers and 'x-retry-count' in properties.headers:
                    retry_count = properties.headers['x-retry-count']

                # Проверяем максимальное количество попыток
                if retry_count >= 3:
                    logger.error(f"Задача превысила максимальное количество попыток ({retry_count})")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    return

                # Создаем worker
                try:
                    worker = self._create_worker()
                    logger.info(f"Worker создан для задачи {task_id}")
                except Exception as e:
                    logger.error(f"Ошибка создания worker: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    time.sleep(5)
                    return

                # Обрабатываем сообщение
                start_time = time.time()
                try:
                    result = worker.process_message(message)
                    processing_time = time.time() - start_time

                    logger.info(f"Задача обработана за {processing_time:.2f} секунд")

                except Exception as e:
                    logger.exception(f"Ошибка обработки сообщения: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    time.sleep(10)
                    return

                # Обработка результата
                if result.get('status') == 'completed':
                    logger.info(f"Задача успешно завершена")
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                elif result.get('status') == 'partial':
                    logger.warning(f"Задача завершена частично: {result.get('error', 'No error info')}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                elif result.get('status') == 'error':
                    error_msg = result.get('error', 'Неизвестная ошибка')
                    logger.error(f"Ошибка обработки задачи: {error_msg}")

                    # Проверяем тип ошибки
                    error_lower = error_msg.lower()

                    # Если AI не смог определить тип компонента - НЕ ПОВТОРЯЕМ
                    if any(phrase in error_lower for phrase in [
                        'не удалось определить тип компонента',
                        'cannot determine component type',
                        'type component not determined',
                        'компонент не определен'
                    ]):
                        logger.warning(f"AI не смог определить тип компонента. Удаляем сообщение из очереди.")
                        ch.basic_ack(delivery_tag=method.delivery_tag)  # Подтверждаем и удаляем

                        # Дополнительно: можно сохранить статистику проблемных запросов
                        self._log_failed_query(message.get('query', ''), error_msg)

                    # Ошибки AI или подключения - повторяем с задержкой
                    elif "ai" in error_lower or "connection" in error_lower or "timeout" in error_lower:
                        logger.info(f"Ошибка AI/подключения. Повтор через 30 секунд")

                        # Обновляем headers
                        new_headers = properties.headers.copy() if properties.headers else {}
                        new_headers['x-retry-count'] = retry_count + 1
                        new_headers['x-last-error'] = error_msg
                        new_headers['x-retry-timestamp'] = int(time.time())

                        # Создаем новые свойства
                        new_properties = pika.BasicProperties(
                            delivery_mode=properties.delivery_mode,
                            content_type=properties.content_type,
                            headers=new_headers,
                            timestamp=int(time.time())
                        )

                        # Отправляем с задержкой
                        delay = min(30, 2 ** retry_count)
                        time.sleep(delay)

                        ch.basic_publish(
                            exchange='',
                            routing_key=self.queue_name,
                            body=body,
                            properties=new_properties
                        )

                        # Подтверждаем оригинальное сообщение
                        ch.basic_ack(delivery_tag=method.delivery_tag)

                    else:
                        # Другие ошибки - не повторяем
                        logger.error(f"Критическая ошибка. Удаляем сообщение из очереди.")
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as e:
            logger.exception(f"Неожиданная ошибка при обработке задачи {task_id}: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            time.sleep(10)

    def _log_failed_query(self, query: str, error: str):
        """Логирование неудачных запросов для анализа"""
        try:
            # Сохраняем в файл для последующего анализа
            log_file = "failed_queries.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] Query: {query}\n")
                f.write(f"[{timestamp}] Error: {error}\n")
                f.write("-" * 80 + "\n")

            logger.info(f"Неудачный запрос сохранен в {log_file}")

        except Exception as e:
            logger.error(f"Ошибка сохранения неудачного запроса: {e}")

    def start_consuming(self):
        """Запуск потребления сообщений из очереди"""
        if self.connection is None or self.connection.is_closed:
            if not self._reconnect():
                raise RuntimeError("Невозможно начать потребление: ошибка подключения")

        try:
            # Настраиваем QoS
            self.channel.basic_qos(prefetch_count=self.prefetch_count)

            # Запускаем consumer
            self.consumer_tag = self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self._callback,
                auto_ack=False,
                consumer_tag=f"consumer_{os.getpid()}_{int(time.time())}"
            )

            self.is_consuming = True
            logger.info(f"Начато потребление из очереди '{self.queue_name}'")

            # Запускаем бесконечный цикл
            self.channel.start_consuming()

        except pika.exceptions.ChannelClosedByBroker as e:
            logger.error(f"Канал закрыт брокером: {e}")
            if self.should_reconnect:
                self._reconnect()
                self.start_consuming()
        except Exception as e:
            logger.error(f"Ошибка запуска consumer: {e}")
            raise

    def stop(self):
        """Graceful остановка потребителя"""
        logger.info("Остановка consumer...")
        self.is_consuming = False
        self.should_reconnect = False

        try:
            # Отменяем consumer
            if self.channel and self.channel.is_open and self.consumer_tag:
                self.channel.basic_cancel(self.consumer_tag)
                logger.info(f"Consumer {self.consumer_tag} отменен")

        except Exception as e:
            logger.error(f"Ошибка отмены consumer: {e}")

        try:
            # Закрываем канал
            if self.channel and self.channel.is_open:
                self.channel.close()

        except Exception as e:
            logger.error(f"Ошибка закрытия канала: {e}")

        try:
            # Закрываем соединение
            if self.connection and self.connection.is_open:
                self.connection.close()
                logger.info("Соединение закрыто")

        except Exception as e:
            logger.error(f"Ошибка закрытия соединения: {e}")

        logger.info("Consumer остановлен")

    def run(self):
        """
        Основной метод запуска consumer'а.
        Обрабатывает KeyboardInterrupt для graceful shutdown.
        """
        try:
            self.start_consuming()
        except KeyboardInterrupt:
            logger.info("Consumer прерван пользователем")
            self.stop()
        except Exception as e:
            logger.error(f"Consumer завершился с ошибкой: {e}")
            self.stop()
            raise

        def _log_failed_query(self, query: str, error: str):
            """Логирование неудачных запросов для анализа"""
            try:
                # Сохраняем в файл для последующего анализа
                log_file = "failed_queries.log"
                with open(log_file, 'a', encoding='utf-8') as f:
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"[{timestamp}] Query: {query}\n")
                    f.write(f"[{timestamp}] Error: {error}\n")
                    f.write("-" * 80 + "\n")

                logger.info(f"Неудачный запрос сохранен в {log_file}")

            except Exception as e:
                logger.error(f"Ошибка сохранения неудачного запроса: {e}")