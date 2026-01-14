# run_consumer.py
import sys
import os
import logging

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка логирования (без поля task_id для глобальных логов)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from consumer import RMQConsumer


def main():
    """Запуск consumer"""
    logger = logging.getLogger(__name__)

    try:
        logger.info("Запуск RabbitMQ Consumer...")

        # Создаем consumer с настройками
        consumer = RMQConsumer(
            host=os.getenv("RABBITMQ_HOST", "localhost"),
            port=int(os.getenv("RABBITMQ_PORT", 5672)),
            queue_name=os.getenv("RABBITMQ_QUEUE", "search_queue"),
            #max_reconnect_attempts=5,
            #prefetch_count=1,
            #recreate_queue=True  # Пересоздать очередь если есть проблемы
        )

        # Запускаем consumer
        consumer.run()

    except KeyboardInterrupt:
        logger.info("Consumer остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка запуска consumer: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()