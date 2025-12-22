# backend/messaging/producer.py

import pika
import json
import os

class RMQProducer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.getenv("RABBITMQ_HOST", "localhost"),
                port=os.getenv("RABBITMQ_PORT", 5672)
            )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='search_queue', durable=True)

    def send_message(self, message: dict):
        self.channel.basic_publish(
            exchange='',
            routing_key='search_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # persistent
        )

    def close(self):
        self.connection.close()