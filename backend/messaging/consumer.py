# backend/messaging/consumer.py

import pika
import json
import os
from .worker import RMQWorker

class RMQConsumer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.getenv("RABBITMQ_HOST", "localhost"),
                port=os.getenv("RABBITMQ_PORT", 5672)
            )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='search_queue', durable=True)

    def start_consuming(self):
        def callback(ch, method, properties, body):
            message = json.loads(body)
            worker = RMQWorker()
            result = worker.process_message(message)
            # TODO: отправить результат обратно (в очередь или веб-сокет)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='search_queue', on_message_callback=callback)
        print("Waiting for messages...")
        self.channel.start_consuming()