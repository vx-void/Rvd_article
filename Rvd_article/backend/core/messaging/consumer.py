import json
import pika
from typing import Callable, Optional

from .message import Message


class RabbitMQConsumer:
    """
    Консьюмер сообщений из очереди.
    Используется в отдельном процессе-воркере.
    """

    def __init__(
        self,
        host: str,
        queue_name: str,
        callback: Callable[[Message], None],
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> None:
        self._host = host
        self._queue_name = queue_name
        self._callback = callback
        self._username = username
        self._password = password

        self._connection = None
        self._channel = None

    def _on_message(self, ch, method, properties, body) -> None:
        """
        Внутренний обработчик получения сообщения.
        """
        try:
            data = json.loads(body.decode())
            message = Message.from_dict(data)

            self._callback(message)

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start(self) -> None:
        """
        Запуск прослушивания очереди.
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

        self._channel.basic_qos(prefetch_count=1)

        self._channel.basic_consume(
            queue=self._queue_name,
            on_message_callback=self._on_message
        )

        self._channel.start_consuming()

    def stop(self) -> None:
        """
        Остановка консьюмера.
        """
        if self._connection:
            self._connection.close()
