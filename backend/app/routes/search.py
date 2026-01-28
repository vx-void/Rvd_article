from flask import Blueprint, request, send_file, current_app
import hashlib
import uuid
import logging
import time
import pandas as pd
from io import BytesIO
from typing import Dict, Any

from backend.utils.responses import SuccessResponse, ErrorResponse
from backend.app.services.rmq_producer import RMQProducer
# Настройка логирования.
logger = logging.getLogger(__name__)

search_bp = Blueprint('search', __name__)

# Сервисы будут инициализироваться при первом использовании
_producer = None

def get_producer() -> RMQProducer:
    """Lazy loading для RMQProducer"""
    global _producer
    if _producer is None:
        _producer = RMQProducer(
            host=current_app.config.get('RABBITMQ_HOST', 'localhost'),
            port=current_app.config.get('RABBITMQ_PORT', 5672),
            queue_name=current_app.config.get('RABBITMQ_QUEUE', 'search_queue')
        )
        logger.info("RMQProducer инициализирован")
    return _producer

@search_bp.route('/', methods=['POST'])
def search():
    """Обработка одиночного поискового запроса"""
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse("Требуется JSON данные", 400).to_response()

        query = data.get('query', '').strip()
        if not query:
            return ErrorResponse("Запрос не может быть пустым", 400).to_response()

        # Генерация идентификаторов
        task_id = str(uuid.uuid4())

        logger.info(f"Обработка запроса", extra={
            'task_id': task_id,
            'query_length': len(query),
        })



        # Подготовка сообщения для single запроса
        message = {
            "task_id": task_id,
            "query": query,
            "type": "single",
            "priority": data.get('priority', 5),
            "metadata": {}
        }

        # Отправка задачи в RabbitMQ
        producer = get_producer()
        success = producer.send_message(message)

        if not success:
            logger.error(f"Не удалось отправить сообщение в RabbitMQ", extra={'task_id': task_id})
            return ErrorResponse(
                message="Не удалось создать задачу обработки",
                status_code=500,
                details={"error": "RabbitMQ отправка не удалась"}
            ).to_response()



        logger.info(f"Задача создана", extra={'task_id': task_id})

        return SuccessResponse({
            "task_id": task_id,
            "status": "processing",
            "type": "single",
            "message": "Поисковая задача создана",
            "check_status_url": f"/api/task/{task_id}"
        }, request_id=task_id).to_response()

    except Exception as e:
        logger.exception(f"Неожиданная ошибка в обработчике поиска: {e}")
        return ErrorResponse(
            message="Внутренняя ошибка сервера",
            status_code=500,
            details={"error": str(e)}
        ).to_response()


@search_bp.route('/batch', methods=['POST'])
def batch_search():
    """Пакетная обработка запросов с AI разбиением"""
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse("Требуется JSON данные", 400).to_response()

        text = data.get('text', '').strip()
        if not text:
            return ErrorResponse("Текст не может быть пустым", 400).to_response()

        # Генерация идентификатора задачи
        task_id = str(uuid.uuid4())

        logger.info(f"Начало пакетной обработки", extra={
            'task_id': task_id,
            'text_length': len(text),
        })


        message = {
            "task_id": task_id,
            "text": text,
            "type": "batch",
            "priority": data.get('priority', 5),
            "metadata": {}
        }

        # Отправка задачи в RabbitMQ
        producer = get_producer()
        success = producer.send_message(message)

        if not success:
            logger.error(f"Не удалось отправить batch сообщение в RabbitMQ", extra={'task_id': task_id})
            return ErrorResponse(
                message="Не удалось создать пакетную задачу",
                status_code=500
            ).to_response()


        logger.info(f"Пакетная задача создана", extra={'task_id': task_id})

        # Возвращаем ответ с task_id на верхнем уровне
        return SuccessResponse({
            "task_id": task_id,
            "status": "processing",
            "type": "batch",
            "message": "Пакетная задача создана",
            "check_status_url": f"/api/task/{task_id}"
        }, request_id=task_id).to_response()

    except Exception as e:
        logger.exception(f"Неожиданная ошибка в пакетной обработке: {e}")
        return ErrorResponse(
            message="Внутренняя ошибка сервера",
            status_code=500,
            details={"error": str(e)}
        ).to_response()

