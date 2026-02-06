import json
import pika
from typing import Optional

from .message import Message


class RabbitMQProducer:
    """
    Реализация брокера сообщений для публикации задач.
    """

    def __init__(
        self,
        host: str,
        queue_name: str,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> None:
        self._host = host
        self._queue_name = queue_name
        self._username = username
        self._password = password

        self._connection = None
        self._channel = None

    def connect(self) -> None:
        """
        Установление соединения с RabbitMQ.
        """
        credentials = None
        if self._username and self._password:
            credentials = pika.PlainCredentials(
                self._username,
                self._password
            )

        parameters = pika.ConnectionParameters(
            host=self._host,
            credentials=credentials
        )

        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()
        self._channel.queue_declare(
            queue=self._queue_name,
            durable=True
        )

    def publish(self, message: dict) -> None:
        """
        Публикация сообщения в очередь.
        """
        if self._channel is None:
            raise RuntimeError("RabbitMQProducer is not connected")

        body = json.dumps(message)

        self._channel.basic_publish(
            exchange="",
            routing_key=self._queue_name,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2  # persistent message
            )
        )

    def close(self) -> None:
        """
        Закрытие соединения.
        """
        if self._connection:
            self._connection.close()
