# backend/app/workers/rmq_worker_windows.py

import os
import pika
import json
import logging
import time
import socket
import platform
from datetime import datetime
import sys

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WindowsRabbitMQWorker:
    """Worker для RabbitMQ в Windows/Docker Desktop"""

    def __init__(self):
        self.connection = None
        self.channel = None
        self.system = platform.system()
        logger.info(f"🚀 Инициализация RabbitMQ Worker для {self.system}")

    def get_connection_params(self):
        """Получение параметров подключения для Windows/Docker Desktop"""

        # Определяем хост в зависимости от того, где запущен worker
        in_docker = os.path.exists('/.dockerenv')

        if self.system == 'Windows':
            if in_docker:
                # Worker в контейнере, RabbitMQ на хосте
                rabbitmq_host = 'host.docker.internal'
            else:
                # Worker на хосте Windows, RabbitMQ в контейнере
                rabbitmq_host = 'localhost'
        else:
            rabbitmq_host = 'localhost'

        # Используем переменные окружения или значения по умолчанию
        host = os.getenv('RABBITMQ_HOST', rabbitmq_host)
        port = int(os.getenv('RABBITMQ_PORT', '5672'))
        username = os.getenv('RABBITMQ_USER', 'guest')
        password = os.getenv('RABBITMQ_PASSWORD', 'guest')

        logger.info(f"Подключение к RabbitMQ: {host}:{port} (Windows: {self.system}, В Docker: {in_docker})")

        credentials = pika.PlainCredentials(username, password)
        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300,
            connection_attempts=5,  # Больше попыток для Windows
            retry_delay=5,
            socket_timeout=10
        )

        return parameters

    def check_port(self, host='localhost', port=5672, timeout=2):
        """Проверка доступности порта"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"Ошибка проверки порта: {e}")
            return False

    def wait_for_rabbitmq(self, timeout=120):
        """Ожидание доступности RabbitMQ (дольше для Windows)"""
        params = self.get_connection_params()

        logger.info(f"⏳ Ожидание RabbitMQ на {params.host}:{params.port}...")

        start_time = time.time()
        check_interval = 3

        while time.time() - start_time < timeout:
            if self.check_port(params.host, params.port):
                elapsed = int(time.time() - start_time)
                logger.info(f"✅ RabbitMQ доступен через {elapsed} секунд")
                return True

            elapsed = int(time.time() - start_time)
            logger.info(f"⏳ Проверка... (прошло {elapsed} сек)")
            time.sleep(check_interval)

        logger.error(f"❌ RabbitMQ не доступен за {timeout} секунд")
        return False

    def connect(self):
        """Подключение к RabbitMQ"""

        # Ждем доступности RabbitMQ
        if not self.wait_for_rabbitmq():
            raise ConnectionError("RabbitMQ недоступен")

        params = self.get_connection_params()

        try:
            # Пытаемся подключиться
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()

            # Настраиваем QoS
            self.channel.basic_qos(prefetch_count=1)

            # Настраиваем очереди
            self.setup_queues()

            logger.info("✅ Подключение к RabbitMQ установлено")
            return True

        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"❌ Ошибка подключения AMQP: {e}")

            # Дополнительная диагностика для Windows
            logger.info("\n🔧 Диагностика для Windows/Docker Desktop:")
            logger.info("1. Проверьте что Docker Desktop запущен")
            logger.info("2. Проверьте что контейнер RabbitMQ запущен: docker ps")
            logger.info("3. Проверьте порты: docker port rabbitmq")
            logger.info("4. Попробуйте перезапустить Docker Desktop")
            logger.info("5. Если используете VPN/Proxy, отключите их временно")

            raise
        except Exception as e:
            logger.error(f"❌ Неизвестная ошибка: {e}")
            raise

    def setup_queues(self):
        """Настройка очередей"""
        if not self.channel:
            raise RuntimeError("Канал не создан")

        # Основная очередь для задач
        queue_name = 'search_tasks'
        self.channel.queue_declare(
            queue=queue_name,
            durable=True,
            arguments={
                'x-max-priority': 10
            }
        )

        logger.info(f"📨 Очередь '{queue_name}' создана")

        # Очередь для результатов
        results_queue = 'search_results'
        self.channel.queue_declare(
            queue=results_queue,
            durable=True
        )

        logger.info(f"📊 Очередь результатов '{results_queue}' создана")

    def process_message(self, ch, method, properties, body):
        """Обработка сообщений"""
        try:
            message = json.loads(body.decode('utf-8'))
            task_id = message.get('task_id', 'unknown')

            logger.info(f"📨 Получена задача: {task_id}")

            # Имитация обработки AI
            logger.info(f"🤖 Обработка задачи {task_id}...")
            time.sleep(2)  # Имитация работы

            # Результат обработки
            result = {
                "task_id": task_id,
                "status": "success",
                "message": "Задача успешно обработана",
                "processed_at": datetime.now().isoformat(),
                "worker": f"windows_{self.system}"
            }

            # Отправляем результат
            self.channel.basic_publish(
                exchange='',
                routing_key='search_results',
                body=json.dumps(result),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )

            # Подтверждаем обработку
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"✅ Задача {task_id} обработана")

        except Exception as e:
            logger.error(f"❌ Ошибка обработки: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        """Запуск worker"""
        if not self.connect():
            logger.error("Не удалось подключиться к RabbitMQ")
            return

        # Подписываемся на очередь
        self.channel.basic_consume(
            queue='search_tasks',
            on_message_callback=self.process_message,
            auto_ack=False
        )

        logger.info("👂 Worker запущен. Ожидание задач...")
        logger.info("Нажмите Ctrl+C для остановки")

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("⏹️ Остановка по запросу пользователя")
        finally:
            self.close()

    def close(self):
        """Закрытие соединения"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("🔌 Соединение закрыто")


def send_test_message():
    """Отправка тестового сообщения"""
    try:
        worker = WindowsRabbitMQWorker()

        if worker.connect():
            test_msg = {
                "task_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "query": "Пример поискового запроса",
                "timestamp": datetime.now().isoformat()
            }

            worker.channel.basic_publish(
                exchange='',
                routing_key='search_tasks',
                body=json.dumps(test_msg),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json',
                    priority=1
                )
            )

            logger.info(f"📤 Тестовое сообщение отправлено: {test_msg['task_id']}")
            worker.close()
    except Exception as e:
        logger.error(f"❌ Ошибка отправки теста: {e}")


def check_connection():
    """Проверка подключения"""
    print("=" * 50)
    print("🔍 ПРОВЕРКА ПОДКЛЮЧЕНИЯ RABBITMQ ДЛЯ WINDOWS")
    print("=" * 50)

    import socket

    worker = WindowsRabbitMQWorker()
    params = worker.get_connection_params()

    print(f"\n📡 Параметры подключения:")
    print(f"  Хост: {params.host}")
    print(f"  Порт: {params.port}")
    print(f"  Пользователь: {params.credentials.username}")
    print(f"  ОС: {platform.system()}")
    print(f"  В Docker: {os.path.exists('/.dockerenv')}")

    print("\n🔎 Проверка портов:")

    # Проверяем стандартные порты RabbitMQ
    ports = [
        (5672, "AMQP основной порт"),
        (15672, "Управляющий интерфейс"),
        (4369, "Erlang порт")
    ]

    for port, desc in ports:
        if worker.check_port(params.host, port):
            print(f"  ✅ Порт {port} ({desc}) ОТКРЫТ")
        else:
            print(f"  ❌ Порт {port} ({desc}) ЗАКРЫТ")

    # Пробуем подключиться
    print("\n🔄 Попытка подключения к RabbitMQ...")
    try:
        connection = pika.BlockingConnection(params)
        print("  ✅ ПОДКЛЮЧЕНИЕ УСПЕШНО!")

        # Показываем информацию о соединении
        channel = connection.channel()
        print(f"  📊 Канал открыт: {channel.is_open}")

        connection.close()
        print("  🔌 Соединение закрыто")

        return True
    except Exception as e:
        print(f"  ❌ ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")

        print("\n🔧 РЕКОМЕНДАЦИИ ДЛЯ WINDOWS:")
        print("1. Убедитесь что Docker Desktop запущен")
        print(
            "2. Запустите RabbitMQ: docker run -d -p 5672:5672 -p 15672:15672 --name rabbitmq rabbitmq:3.12-management")
        print("3. Проверьте: docker ps")
        print("4. Откройте веб-интерфейс: http://localhost:15672 (guest/guest)")
        print("5. Если есть VPN, попробуйте отключить")
        print("6. Проверьте брандмауэр Windows")

        return False


def main():
    """Основная функция"""

    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            send_test_message()
            return
        elif sys.argv[1] == '--check':
            check_connection()
            return
        elif sys.argv[1] == '--help':
            print("Использование:")
            print("  python rmq_worker_windows.py          # Запуск worker")
            print("  python rmq_worker_windows.py --test   # Отправить тест")
            print("  python rmq_worker_windows.py --check  # Проверить подключение")
            print("  python rmq_worker_windows.py --help   # Эта справка")
            return

    # Запуск worker
    worker = WindowsRabbitMQWorker()

    while True:
        try:
            worker.start()
        except KeyboardInterrupt:
            logger.info("👋 Завершение работы")
            break
        except Exception as e:
            logger.error(f" Ошибка: {e}")
            logger.info("♻️ Перезапуск через 10 секунд...")
            time.sleep(10)
            worker = WindowsRabbitMQWorker()  # Создаем новый экземпляр


if __name__ == "__main__":
    main()