from flask import Blueprint, request, jsonify
import hashlib
import uuid
import os
from ..services.cache_service import CacheService
from ..messaging.producer import RMQProducer
from ..utils.responses import success_response, error_response

search_bp = Blueprint('search', __name__)
cache_service = CacheService()


@search_bp.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query', '').strip()

    if not query:
        return error_response("Query is required", 400)


    task_id = str(uuid.uuid4())

    query_hash = hashlib.md5(query.encode()).hexdigest()
    cached_result = cache_service.get_cached_search_result(query_hash)

    if cached_result:
        return success_response({
            "task_id": task_id,
            "source": "cache",
            "matches": cached_result
        })

    # Создаем асинхронную задачу
    message = {
        "task_id": task_id,
        "query": query,
        "quantity": data.get('quantity', 1)
    }

    producer = RMQProducer()
    producer.send_message(message)
    producer.close()

    # Сохраняем начальный статус задачи
    cache_service.set_task_status(task_id, "processing")

    return success_response({
        "task_id": task_id,
        "status": "processing",
        "message": "Search task created"
    })


@search_bp.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task_status = cache_service.get_task_status(task_id)

    if not task_status:
        return error_response("Task not found", 404)

    return success_response({
        "task_id": task_id,
        "status": task_status.get("status"),
        "result": task_status.get("result")
    })


@search_bp.route('/download/<task_id>', methods=['GET'])
def download_excel(task_id):
    excel_path = cache_service.get_cached_excel_path(task_id)

    if not excel_path or not os.path.exists(excel_path):
        return error_response("Excel file not found", 404)

    # Здесь должна быть логика отправки файла
    # Например: return send_file(excel_path, as_attachment=True)

    return success_response({
        "path": excel_path,
        "filename": os.path.basename(excel_path)
    })