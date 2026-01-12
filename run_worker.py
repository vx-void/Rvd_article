# run_worker.py
from backend.messaging.consumer import RMQConsumer
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    consumer = RMQConsumer()
    try:
        consumer.start_consuming()
    except KeyboardInterrupt:
        consumer.stop()
        print("\n Worker остановлен.")