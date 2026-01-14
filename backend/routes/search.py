from flask import Blueprint, request, send_file, current_app
import hashlib
import uuid
import logging
from typing import Dict, Any

from ..services.cache_service import CacheService
from ..messaging.producer import RMQProducer
from ..utils.responses import SuccessResponse, ErrorResponse

# Настройка логирования
logger = logging.getLogger(__name__)

search_bp = Blueprint('search', __name__)

# Сервисы будут инициализироваться при первом использовании
_cache_service = None
_producer = None


def get_cache_service() -> CacheService:
    """Lazy loading для CacheService"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
        logger.info("CacheService инициализирован")
    return _cache_service


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
    """Обработка поискового запроса"""
    try:
        data = request.get_json()
        if not data:
            return ErrorResponse("Требуется JSON данные", 400).to_response()

        query = data.get('query', '').strip()
        if not query:
            return ErrorResponse("Запрос не может быть пустым", 400).to_response()

        # Генерация идентификаторов
        task_id = str(uuid.uuid4())

        # Используем SHA256 вместо MD5 для безопасности
        query_hash = hashlib.sha256(query.encode()).hexdigest()

        logger.info(f"Обработка запроса", extra={
            'task_id': task_id,
            'query_length': len(query),
            'query_hash': query_hash[:16]  # Только первые 16 символов для логов
        })

        # Получаем сервисы
        cache_service = get_cache_service()

        # Проверка кэша
        cached_result = cache_service.get_cached_search_result(query_hash)
        if cached_result:
            logger.info(f"Результат найден в кэше", extra={'task_id': task_id})
            return SuccessResponse({
                "task_id": task_id,
                "source": "cache",
                "matches": cached_result,
                "cached": True
            }, request_id=task_id).to_response()

        # Подготовка сообщения
        message = {
            "task_id": task_id,
            "query": query,
            "quantity": data.get('quantity', 1),
            "priority": data.get('priority', 5)
        }

        # Добавляем опциональные поля
        optional_fields = ['metadata', 'callback_url', 'user_id']
        for field in optional_fields:
            if field in data:
                message[field] = data[field]

        # Отправка задачи в RabbitMQ
        try:
            producer = get_producer()
            success = producer.send_message(message)

            if not success:
                logger.error(f"Не удалось отправить сообщение в RabbitMQ", extra={'task_id': task_id})
                return ErrorResponse(
                    message="Не удалось создать задачу обработки",
                    status_code=500,
                    details={"error": "RabbitMQ отправка не удалась"}
                ).to_response()

        except Exception as e:
            logger.exception(f"Ошибка при отправке в RabbitMQ: {e}", extra={'task_id': task_id})
            return ErrorResponse(
                message=f"Ошибка создания задачи: {str(e)}",
                status_code=500,
                details={"error_type": type(e).__name__}
            ).to_response()

        # Сохранение начального статуса задачи
        cache_service.set_task_status(task_id, "processing", {
            "query": query,
            "created_at": task_id  # Используем timestamp из UUID
        })

        logger.info(f"Задача создана", extra={'task_id': task_id})

        return SuccessResponse({
            "task_id": task_id,
            "status": "processing",
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


@search_bp.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Получение статуса задачи"""
    try:
        # Валидация task_id
        try:
            uuid.UUID(task_id)
        except ValueError:
            return ErrorResponse(
                message="Некорректный идентификатор задачи",
                status_code=400,
                details={"task_id": task_id}
            ).to_response()

        cache_service = get_cache_service()
        task_status = cache_service.get_task_status(task_id)

        if not task_status:
            logger.warning(f"Задача не найдена", extra={'task_id': task_id})
            return ErrorResponse(
                message=f"Задача {task_id} не найдена",
                status_code=404,
                details={
                    "task_id": task_id,
                    "hint": "Задача могла быть удалена или время ее жизни истекло"
                }
            ).to_response()

        logger.debug(f"Статус задачи получен", extra={
            'task_id': task_id,
            'status': task_status.get('status')
        })

        response_data = {
            "task_id": task_id,
            "status": task_status.get("status"),
            "result": task_status.get("result"),
            "timestamp": task_status.get("timestamp")
        }

        # Добавляем дополнительные поля если есть
        if "query" in task_status.get("result", {}):
            response_data["query"] = task_status["result"]["query"]

        return SuccessResponse(response_data, request_id=task_id).to_response()

    except Exception as e:
        logger.exception(f"Ошибка при получении статуса задачи {task_id}: {e}")
        return ErrorResponse(
            message="Ошибка при получении статуса задачи",
            status_code=500,
            details={"task_id": task_id, "error": str(e)}
        ).to_response()


@search_bp.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья поискового сервиса"""
    try:
        # Проверяем соединение с кэшем
        cache_service = get_cache_service()
        cache_ok = False
        try:
            # Простая проверка Redis
            cache_service._redis.ping()
            cache_ok = True
        except Exception as e:
            logger.error(f"Ошибка подключения к Redis: {e}")

        # Проверяем соединение с RabbitMQ
        rabbitmq_ok = False
        try:
            producer = get_producer()
            # Пытаемся создать тестовое сообщение
            test_message = producer.create_message("health_check", priority=0)
            rabbitmq_ok = True
        except Exception as e:
            logger.error(f"Ошибка подключения к RabbitMQ: {e}")

        health_status = "healthy" if cache_ok and rabbitmq_ok else "degraded"

        return SuccessResponse({
            "status": health_status,
            "services": {
                "cache": "healthy" if cache_ok else "unhealthy",
                "rabbitmq": "healthy" if rabbitmq_ok else "unhealthy"
            },
            "timestamp": str(uuid.uuid1().time)
        }).to_response()

    except Exception as e:
        logger.exception(f"Ошибка health check: {e}")
        return ErrorResponse(
            message="Ошибка проверки здоровья",
            status_code=500
        ).to_response()