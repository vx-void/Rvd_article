from flask import Blueprint, request, send_file
import hashlib
import uuid
import os

from ..services.cache_service import CacheService
from ..messaging.producer import RMQProducer
from ..utils.responses import SuccessResponse, ErrorResponse

search_bp = Blueprint('search', __name__)
cache_service = CacheService()


@search_bp.route('/', methods=['POST'])
def search():
    data = request.get_json()
    if not data:
        return ErrorResponse("JSON data required", 400).to_response()

    query = data.get('query', '').strip()
    if not query:
        return ErrorResponse("Query is required", 400).to_response()

    task_id = str(uuid.uuid4())
    query_hash = hashlib.md5(query.encode()).hexdigest()

    # Проверка кэша
    cached_result = cache_service.get_cached_search_result(query_hash)
    if cached_result:
        return SuccessResponse({
            "task_id": task_id,
            "source": "cache",
            "matches": cached_result
        }, request_id=task_id).to_response()

    # Создание асинхронной задачи
    message = {
        "task_id": task_id,
        "query": query,
        "quantity": data.get('quantity', 1)
    }

    try:
        producer = RMQProducer()
        producer.send_message(message)
        producer.close()
    except Exception as e:
        return ErrorResponse(f"Failed to create task: {str(e)}", 500).to_response()

    # Сохранение статуса задачи
    cache_service.set_task_status(task_id, "processing")

    return SuccessResponse({
        "task_id": task_id,
        "status": "processing",
        "message": "Search task created"
    }, request_id=task_id).to_response()


@search_bp.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task_status = cache_service.get_task_status(task_id)

    if not task_status:
        return ErrorResponse(
            message=f"Task {task_id} not found",
            status_code=404,
            details={"task_id": task_id}
        ).to_response()

    return SuccessResponse({
        "task_id": task_id,
        "status": task_status.get("status"),
        "result": task_status.get("result")
    }, request_id=task_id).to_response()


@search_bp.route('/download/<task_id>', methods=['GET'])
def download_excel(task_id):
    excel_path = cache_service.get_cached_excel_path(task_id)

    if not excel_path or not os.path.exists(excel_path):
        return ErrorResponse(f"Excel file for task {task_id} not found", 404).to_response()

    return send_file(
        excel_path,
        as_attachment=True,
        download_name=f"results_{task_id[:8]}.xlsx"
    )