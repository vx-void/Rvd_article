from flask import Blueprint, request, send_file, current_app
import hashlib
import uuid
import logging
import time
import pandas as pd
from io import BytesIO
from typing import Dict, Any

from backend.app.services import CacheService
from ..messaging.producer import RMQProducer
from backend.utils.responses import SuccessResponse, ErrorResponse

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

        # Получаем сервисы
        cache_service = get_cache_service()

        # Проверка кэша
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        cached_result = cache_service.get_cached_search_result(query_hash)
        if cached_result:
            logger.info(f"Результат найден в кэше", extra={'task_id': task_id})
            return SuccessResponse({
                "task_id": task_id,
                "status": "completed",
                "source": "cache",
                "type": "single",
                "result": cached_result
            }, request_id=task_id).to_response()

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

        # Сохранение начального статуса задачи
        cache_service.set_task_status(task_id, "processing", {
            "query": query,
            "type": "single",
            "created_at": time.time()
        })

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

        # Получаем сервисы
        cache_service = get_cache_service()

        # Проверка кэша
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        cached_result = cache_service.get_cached_search_result(text_hash)
        if cached_result:
            logger.info(f"Batch результат найден в кэше", extra={'task_id': task_id})
            # Возвращаем сразу с task_id на верхнем уровне
            return SuccessResponse({
                "task_id": task_id,
                "status": "completed",
                "source": "cache",
                "type": "batch",
                "result": cached_result
            }, request_id=task_id).to_response()

        # Подготовка сообщения для batch запроса
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

        # Сохранение начального статуса задачи
        cache_service.set_task_status(task_id, "processing", {
            "text": text,
            "type": "batch",
            "created_at": time.time()
        })

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


@search_bp.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Получение статуса задачи с авто-завершением старых задач"""
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

        # Проверяем время создания задачи
        created_at = task_status.get('result', {}).get('created_at') or task_status.get('created_at')
        current_time = time.time()

        # Если задача в статусе "processing" больше 5 минут - отмечаем как "timeout"
        if (task_status.get('status') == 'processing' and
                created_at and
                (current_time - created_at) > 300):  # 5 минут

            logger.warning(f"Задача {task_id} превысила timeout (5 минут)", extra={'task_id': task_id})

            # Обновляем статус на timeout
            timeout_result = {
                "error": "Превышено время обработки (5 минут)",
                "status": "timeout",
                "task_id": task_id,
                "created_at": created_at,
                "timeout_at": current_time
            }

            cache_service.set_task_status(task_id, "timeout", timeout_result)

            return SuccessResponse({
                "task_id": task_id,
                "status": "timeout",
                "result": timeout_result,
                "message": "Задача превысила максимальное время обработки"
            }, request_id=task_id).to_response()

        logger.debug(f"Статус задачи получен", extra={
            'task_id': task_id,
            'status': task_status.get('status'),
            'age_seconds': current_time - created_at if created_at else 'unknown'
        })

        response_data = {
            "task_id": task_id,
            "status": task_status.get("status"),
            "result": task_status.get("result"),
            "type": task_status.get("result", {}).get("type", "single") if task_status.get("result") else "single",
            "timestamp": task_status.get("updated_at"),
            "age_seconds": current_time - created_at if created_at else None
        }

        return SuccessResponse(response_data, request_id=task_id).to_response()

    except Exception as e:
        logger.exception(f"Ошибка при получении статуса задачи {task_id}: {e}")
        return ErrorResponse(
            message="Ошибка при получении статуса задачи",
            status_code=500,
            details={"task_id": task_id, "error": str(e)}
        ).to_response()


@search_bp.route('/download/<task_id>', methods=['GET'])
def download_excel(task_id):
    """Скачивание результатов в формате Excel"""
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
            return ErrorResponse(
                message=f"Задача {task_id} не найдена",
                status_code=404
            ).to_response()

        if task_status.get('status') != 'completed':
            return ErrorResponse(
                message=f"Задача еще не завершена. Статус: {task_status.get('status')}",
                status_code=400
            ).to_response()

        # Получаем результаты
        result_data = task_status.get('result', {})
        if not result_data:
            return ErrorResponse(
                message="Нет данных для экспорта",
                status_code=404
            ).to_response()

        # Генерируем Excel
        excel_data = _generate_excel_data(result_data)

        # Создаем Excel файл в памяти
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            excel_data.to_excel(writer, sheet_name='Результаты поиска', index=False)
            worksheet = writer.sheets['Результаты поиска']

            # Настройка ширины колонок
            worksheet.column_dimensions['A'].width = 40  # Запрос
            worksheet.column_dimensions['B'].width = 50  # Наименование
            worksheet.column_dimensions['C'].width = 20  # Артикул
            worksheet.column_dimensions['D'].width = 10  # Количество

        buffer.seek(0)

        # Генерация имени файла
        filename = f"результаты_поиска_{task_id[:8]}.xlsx"

        logger.info(f"Excel файл сгенерирован для задачи {task_id}", extra={
            'task_id': task_id,
            'rows_count': len(excel_data)
        })

        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.exception(f"Ошибка генерации Excel для задачи {task_id}: {e}")
        return ErrorResponse(
            message="Ошибка генерации Excel файла",
            status_code=500,
            details={"error": str(e)}
        ).to_response()


def _generate_excel_data(result_data: Dict[str, Any]) -> pd.DataFrame:
    """Генерация данных для Excel"""
    rows = []

    # Проверяем тип результата (single или batch)
    is_batch = result_data.get('type') == 'batch'

    if is_batch:
        # Обработка batch результатов
        for item in result_data.get('results', []):
            query = item.get('original_query', '')
            quantity = item.get('quantity', 1)

            matches = item.get('matches', [])
            if matches:
                for match in matches:
                    rows.append({
                        'Запрос': query,
                        'Наименование': match.get('name', ''),
                        'Артикул': match.get('article', ''),
                        'Количество': quantity
                    })
            else:
                rows.append({
                    'Запрос': query,
                    'Наименование': 'Не найден',
                    'Артикул': '',
                    'Количество': quantity
                })
    else:
        # Обработка single результата
        query = result_data.get('query', '')
        matches = result_data.get('matches', [])
        quantity = result_data.get('quantity', 1)

        if matches:
            for match in matches:
                rows.append({
                    'Запрос': query,
                    'Наименование': match.get('name', ''),
                    'Артикул': match.get('article', ''),
                    'Количество': quantity
                })
        else:
            rows.append({
                'Запрос': query,
                'Наименование': 'Не найден',
                'Артикул': '',
                'Количество': quantity
            })

    # Создаем DataFrame с правильным порядком колонок
    df = pd.DataFrame(rows, columns=['Запрос', 'Наименование', 'Артикул', 'Количество'])
    return df


@search_bp.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья поискового сервиса"""
    try:
        # Проверяем соединение с кэшем
        cache_service = get_cache_service()
        cache_ok = False
        try:
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
            "timestamp": time.time()
        }).to_response()

    except Exception as e:
        logger.exception(f"Ошибка health check: {e}")
        return ErrorResponse(
            message="Ошибка проверки здоровья",
            status_code=500
        ).to_response()


@search_bp.route('/task/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """Ручная отмена задачи (принудительное завершение)"""
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
            return ErrorResponse(
                message=f"Задача {task_id} не найдена",
                status_code=404
            ).to_response()

        # Если задача еще в обработке - помечаем как отмененную
        if task_status.get('status') == 'processing':
            canceled_result = {
                "error": "Задача отменена пользователем (worker не ответил)",
                "status": "canceled",
                "task_id": task_id,
                "canceled_at": time.time(),
                "original_status": task_status
            }

            cache_service.set_task_status(task_id, "canceled", canceled_result)

            logger.warning(f"Задача {task_id} отменена пользователем")

            return SuccessResponse({
                "task_id": task_id,
                "status": "canceled",
                "message": "Задача отменена"
            }, request_id=task_id).to_response()
        else:
            # Задача уже завершена или отменена
            return SuccessResponse({
                "task_id": task_id,
                "status": task_status.get('status'),
                "message": f"Задача уже в статусе: {task_status.get('status')}"
            }, request_id=task_id).to_response()

    except Exception as e:
        logger.exception(f"Ошибка отмены задачи {task_id}: {e}")
        return ErrorResponse(
            message="Ошибка отмены задачи",
            status_code=500,
            details={"task_id": task_id, "error": str(e)}
        ).to_response()