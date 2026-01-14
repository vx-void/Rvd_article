import pika
import json
import os
import time
import logging
import threading
import uuid
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, asdict
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Датакласс для структурированных сообщений"""
    task_id: str
    query: str
    priority: int = 5
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None

    def __post_init__(self):
        """Инициализация после создания датакласса"""
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}
        if not isinstance(self.priority, int) or self.priority < 0 or self.priority > 10:
            raise ValueError("Priority must be an integer between 0 and 10")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return asdict(self)


class RMQProducer:
    """Продюсер сообщений RabbitMQ"""

    def __init__(
            self,
            host: Optional[str] = None,
            port: Optional[int] = None,
            queue_name: str = 'search_queue',
            default_priority: int = 5,
            max_retries: int = 3,
            recreate_queue: bool = False  # Флаг для пересоздания очереди
    ):
        """
        Инициализация продюсера.

        Args:
            host: Хост RabbitMQ (по умолчанию из env RABBITMQ_HOST или localhost)
            port: Порт RabbitMQ (по умолчанию из env RABBITMQ_PORT или 5672)
            queue_name: Имя очереди для отправки сообщений
            default_priority: Приоритет по умолчанию для сообщений
            max_retries: Максимальное количество попыток отправки
            recreate_queue: Пересоздать очередь если параметры не совпадают
        """
        self.host = host or os.getenv("RABBITMQ_HOST", "localhost")
        self.port = port or int(os.getenv("RABBITMQ_PORT", 5672))
        self.queue_name = queue_name
        self.default_priority = default_priority
        self.max_retries = max_retries
        self.recreate_queue = recreate_queue

        # Создаем соединение
        self._connection = None
        self._channel = None
        self._connect_lock = threading.Lock()

        # Инициализация подключения
        self._connect()

        # Регистрация обработчика при завершении
        import atexit
        atexit.register(self.close)

        logger.info(f"Продюсер инициализирован для очереди '{queue_name}'")

    def _connect(self):
        """Подключение к RabbitMQ"""
        with self._connect_lock:
            try:
                if self._connection and not self._connection.is_closed:
                    return

                # Закрываем старые соединения если они есть
                if self._channel and self._channel.is_open:
                    self._channel.close()
                if self._connection and self._connection.is_open:
                    self._connection.close()

                # Создаем новое соединение
                self._connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.host,
                        port=self.port,
                        connection_attempts=3,
                        retry_delay=5,
                        heartbeat=600,
                        socket_timeout=10
                    )
                )

                self._channel = self._connection.channel()

                # Объявляем очередь (без dead-letter параметров для совместимости)
                try:
                    if self.recreate_queue:
                        # Пытаемся удалить старую очередь
                        try:
                            self._channel.queue_delete(self.queue_name)
                            logger.info(f"Очередь {self.queue_name} удалена для пересоздания")
                        except:
                            pass

                    # Создаем очередь с минимальными параметрами
                    self._channel.queue_declare(
                        queue=self.queue_name,
                        durable=True
                    )

                except pika.exceptions.ChannelClosedByBroker as e:
                    # Если очередь уже существует с другими параметрами,
                    # используем пассивное объявление
                    if "PRECONDITION_FAILED" in str(e):
                        logger.warning(f"Очередь {self.queue_name} уже существует с другими параметрами")
                        self._channel = self._connection.channel()
                        self._channel.queue_declare(
                            queue=self.queue_name,
                            durable=True,
                            passive=True  # Только проверка существования
                        )
                    else:
                        raise

                logger.info(f"Успешно подключено к RabbitMQ {self.host}:{self.port}")

            except Exception as e:
                logger.error(f"Ошибка подключения к RabbitMQ: {e}")
                raise

    def _reconnect(self):
        """Повторное подключение"""
        try:
            self._connect()
            return True
        except Exception as e:
            logger.error(f"Ошибка переподключения: {e}")
            return False

    def validate_message(self, message: Union[Dict[str, Any], Message]) -> List[str]:
        """
        Валидация сообщения перед отправкой.

        Args:
            message: Сообщение для валидации

        Returns:
            List[str]: Список ошибок валидации (пустой если ошибок нет)
        """
        errors = []

        # Преобразуем Message в dict если необходимо
        if isinstance(message, Message):
            message_dict = message.to_dict()
        elif isinstance(message, dict):
            message_dict = message
        else:
            errors.append("Сообщение должно быть словарем или объектом Message")
            return errors

        # Проверка обязательных полей
        if 'task_id' not in message_dict:
            errors.append("Отсутствует обязательное поле: task_id")
        elif not isinstance(message_dict['task_id'], str):
            errors.append("task_id должен быть строкой")
        elif not message_dict['task_id'].strip():
            errors.append("task_id не может быть пустым")

        if 'query' not in message_dict:
            errors.append("Отсутствует обязательное поле: query")
        elif not isinstance(message_dict['query'], str):
            errors.append("query должен быть строкой")
        elif not message_dict['query'].strip():
            errors.append("query не может быть пустым")

        # Проверка опциональных полей
        if 'priority' in message_dict:
            priority = message_dict['priority']
            if not isinstance(priority, int):
                errors.append("priority должен быть целым числом")
            elif priority < 0 or priority > 10:
                errors.append("priority должен быть в диапазоне от 0 до 10")

        if 'metadata' in message_dict and not isinstance(message_dict['metadata'], dict):
            errors.append("metadata должен быть словарем")

        return errors

    def create_message(
            self,
            query: str,
            task_id: Optional[str] = None,
            priority: int = 5,
            metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Создание структурированного сообщения.

        Args:
            query: Поисковый запрос
            task_id: Идентификатор задачи (генерируется если не указан)
            priority: Приоритет сообщения (0-10)
            metadata: Дополнительные метаданные

        Returns:
            Message: Структурированное сообщение
        """
        if task_id is None:
            task_id = str(uuid.uuid4())

        return Message(
            task_id=task_id,
            query=query.strip(),
            priority=priority,
            metadata=metadata or {}
        )

    def send_message(
            self,
            message: Union[Dict[str, Any], Message],
            queue_name: Optional[str] = None,
            retry_on_failure: bool = True
    ) -> bool:
        """
        Отправка сообщения в очередь.

        Args:
            message: Сообщение для отправки
            queue_name: Имя очереди (по умолчанию self.queue_name)
            retry_on_failure: Повторять отправку при ошибке

        Returns:
            bool: True если отправка успешна, False в противном случае

        Raises:
            ValueError: Если сообщение невалидно
        """
        if queue_name is None:
            queue_name = self.queue_name

        # Преобразуем Message в dict если необходимо
        if isinstance(message, Message):
            message_dict = message.to_dict()
        else:
            message_dict = message

        # Валидация сообщения
        validation_errors = self.validate_message(message_dict)
        if validation_errors:
            error_msg = f"Ошибки валидации сообщения: {'; '.join(validation_errors)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Подготовка сообщения
        full_message = {
            'task_id': message_dict['task_id'],
            'query': message_dict['query'].strip(),
            'priority': message_dict.get('priority', self.default_priority),
            'metadata': message_dict.get('metadata', {}),
            'timestamp': time.time()
        }

        # Подготовка свойств сообщения
        properties = pika.BasicProperties(
            delivery_mode=2,  # Persistent сообщение
            content_type='application/json',
            content_encoding='utf-8',
            timestamp=int(time.time()),
            priority=full_message['priority'],
            headers={
                'x-sent-timestamp': int(time.time()),
                'x-task-id': full_message['task_id'],
                'x-priority': full_message['priority'],
                'x-retry-count': 0
            }
        )

        # Попытки отправки
        max_attempts = self.max_retries if retry_on_failure else 1

        for attempt in range(max_attempts):
            try:
                # Проверяем и восстанавливаем соединение если нужно
                if not self._channel or not self._channel.is_open:
                    if not self._reconnect():
                        if attempt < max_attempts - 1:
                            time.sleep(2 ** attempt)
                            continue
                        else:
                            return False

                self._channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=json.dumps(full_message, ensure_ascii=False),
                    properties=properties
                )

                logger.info(
                    f"Сообщение отправлено в очередь '{queue_name}'",
                    extra={
                        'task_id': full_message['task_id'],
                        'queue': queue_name,
                        'priority': full_message['priority']
                    }
                )

                return True

            except (pika.exceptions.AMQPConnectionError, pika.exceptions.StreamLostError) as e:
                wait_time = min(30, 2 ** attempt)
                logger.warning(
                    f"Ошибка подключения при отправке сообщения {full_message['task_id']}. "
                    f"Попытка {attempt + 1}/{max_attempts}. Ожидание {wait_time} секунд..."
                )

                if attempt < max_attempts - 1:
                    time.sleep(wait_time)
                    self._reconnect()
                else:
                    logger.error(
                        f"Не удалось отправить сообщение {full_message['task_id']} после {max_attempts} попыток"
                    )
                    return False

            except Exception as e:
                logger.exception(
                    f"Неожиданная ошибка при отправке сообщения {full_message['task_id']}: {e}"
                )
                if attempt == max_attempts - 1:
                    return False
                time.sleep(1)

        return False

    def close(self):
        """Закрытие ресурсов продюсера"""
        logger.info("Закрытие ресурсов продюсера...")

        try:
            if self._channel and self._channel.is_open:
                self._channel.close()
                logger.debug("Канал закрыт")
        except Exception as e:
            logger.error(f"Ошибка закрытия канала: {e}")

        try:
            if self._connection and self._connection.is_open:
                self._connection.close()
                logger.debug("Соединение закрыто")
        except Exception as e:
            logger.error(f"Ошибка закрытия соединения: {e}")

        logger.info("Ресурсы продюсера закрыты")

    def __del__(self):
        """Деструктор"""
        try:
            self.close()
        except:
            pass