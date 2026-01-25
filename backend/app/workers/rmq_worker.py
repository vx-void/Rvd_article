# backend/app/workers/rmq_worker.py

import pika
import json
import logging
# from app.config import Config # Не импортируем сразу
import time

from backend.app.services.ai_service import AIService
from backend.app.services.db_service import DBService
from backend.app.services import excel_service, cache_service
from backend.app.config import Config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Глобальные переменные для подключения ---
connection = None
channel = None

def setup_rabbitmq_connection():
    """Устанавливает подключение к RabbitMQ для воркера."""
    global connection, channel
    from backend.app.config import Config

    #rabbitmq_url = f"amqp://{Config.RABBITMQ_USER}:{Config.RABBITMQ_PASS}@{Config.RABBITMQ_HOST}:{Config.RABBITMQ_PORT}/%2F"
    rabbitmq_url = f"amqp://{Config.RABBITMQ_USER}:{Config.RABBITMQ_PASS}@{Config.RABBITMQ_HOST}:{Config.RABBITMQ_PORT}/{Config.RABBITMQ_VHOST}"
    try:
        connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
        channel = connection.channel()
        channel.queue_declare(queue='article_search_queue', durable=True)
        logger.info(f"[Worker] Connected to queue at {rabbitmq_url}")
    except Exception as e:
        logger.error(f"[Worker] Failed to connect to RabbitMQ: {e}")
        raise

# --- Инициализация внешних сервисов ---
ai_service = AIService()
db_service = DBService()

def callback(ch, method, properties, body):
    """
    Callback-функция для обработки сообщений из очереди RabbitMQ.
    """
    task_data = json.loads(body)
    task_id = task_data['task_id']
    query = task_data['query']

    logger.info(f"[Worker] Processing task {task_id} for query: '{query[:50]}...'")

    cache_service.set_status(task_id, 'processing')

    try:
        logger.debug(f"[Worker] Calling AI service for task {task_id}...")
        extracted_params = ai_service.process_single(query)

        if not extracted_params:
            logger.error(f"[Worker] AI service failed for task {task_id}: process_single returned None or empty.")
            cache_service.set_task_result(task_id, 'failed', {'error': 'AI returned invalid or no data'})
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        logger.info(f"[Worker] AI extracted parameters: {extracted_params}")

        logger.debug(f"[Worker] Calling DB service for task {task_id}...")
        search_results = db_service.search_by_ai_params(extracted_params)

        if not search_results:
            logger.info(f"[Worker] No results found in DB for task {task_id}.")
            cache_service.set_task_result(task_id, 'completed', {'results': [], 'message': 'No matches found in catalog.'})
        else:
            logger.info(f"[Worker] Found {len(search_results)} results in DB for task {task_id}.")
            excel_path = excel_service.generate_report(search_results, query)

            final_result = {
                'results': search_results,
                'summary': f"Found {len(search_results)} items matching the description."
            }

            cache_service.set_task_result(task_id, 'completed', final_result)
            cache_service.set_excel_file_path(task_id, excel_path)

            import hashlib
            query_hash = hashlib.md5(query.encode()).hexdigest()
            cache_service.set_result_in_cache(query_hash, task_id, final_result)

    except Exception as e:
        logger.error(f"[Worker] Error processing task {task_id}: {str(e)}")
        cache_service.set_task_result(task_id, 'failed', {'error': str(e)})

    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"[Worker] Task {task_id} processing finished.")

if __name__ == '__main__':
    # Устанавливаем подключение *после* запуска скрипта, когда Config уже может быть доступна
    setup_rabbitmq_connection()

    logger.info("[Worker] Starting RabbitMQ consumer...")
    channel.basic_consume(queue='article_search_queue', on_message_callback=callback)
    logger.info("[Worker] Waiting for messages. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Interrupted. Closing connection...")
        channel.stop_consuming()
        connection.close()
        logger.info("Connection closed.")
