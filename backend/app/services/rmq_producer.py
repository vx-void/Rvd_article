# backend/app/services/rmq_producer.py

import pika
import json
# Не импортируем Config здесь, чтобы избежать проблем при импорте
# from app.config import Config


class RMQProducer:
    _connection = None
    _channel = None

    def _ensure_connection(self):
        """
        Устанавливает подключение к RabbitMQ, если оно ещё не установлено.
        Использует значения из app.config.Config.
        """

        if self._channel is not None and self._channel_channel.is_open:
            return # Подключение уже активно

    # Импортируем Config *внутри функции*, чтобы убедиться, что она инициализирована
        from backend.app.config import Config

    # Формируем URL для pika
    # Читаем параметры из Config
        user = Config.RABBITMQ_USER
        password = Config.RABBITMQ_PASS
        host = Config.RABBITMQ_HOST
        port = Config.RABBITMQ_PORT

    # Формируем URL для pika. Явно указываем vhost как /
    # Важно: слэш нужно экранировать в URL, поэтому %2F
        rabbitmq_url = f"amqp://{user}:{password}@{host}:{port}/%2F"


        try:
        # Закрываем старое соединение, если оно было
            if self._connection and not self._connection.is_closed:
                self._connection.close()

        # Создаём новое подключение
            _connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
            _channel = _connection.channel()

        # Убеждаемся, что очередь существует
            _channel.queue_declare(queue='article_search_queue', durable=True)
            print(f"[RMQ Producer] Connected to queue at {rabbitmq_url}")
        except Exception as e:
            print(f"[RMQ Producer] Failed to connect to RabbitMQ: {e}")
            raise # Пробрасываем ошибку, чтобы вызывающая сторона могла обработать

    def send_task(self, task_id: str, query: str):

        """
        Отправляет задачу в очередь RabbitMQ.
        """
        # Убедиться, что подключение установлено

        self._ensure_connection()

        message = {
            'task_id': task_id,
            'query': query
        }
        self._channel.basic_publish(
            exchange='',
            routing_key='article_search_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
        )
        print(f"[RMQ Producer] Sent task {task_id} to queue.")
