import pika
import json
import os
import logging
import psycopg2
from .worker import RMQWorker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RMQConsumer:
    def __init__(self):
        self.host = os.getenv("RABBITMQ_HOST", "localhost")
        self.port = int(os.getenv("RABBITMQ_PORT", 5672))
        self._connect()

    def _connect(self):
        """Установка соединения с RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    heartbeat=600
                )
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='search_queue', durable=True)
            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def _callback(self, ch, method, properties, body):
        """Обработка сообщения из очереди"""
        try:
            message = json.loads(body)
            logger.info(f"Processing task: {message.get('task_id')}")

            worker = RMQWorker()
            result = worker.process_message(message)

            # Подтверждение обработки
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Task {message.get('task_id')} completed")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self):
        """Запуск потребителя"""
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue='search_queue',
            on_message_callback=self._callback
        )
        logger.info("Waiting for messages...")
        self.channel.start_consuming()

    def stop(self):
        """Остановка потребителя"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")