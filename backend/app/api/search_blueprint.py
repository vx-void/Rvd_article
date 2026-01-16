# backend/app/api/search_blueprint.py

from flask import Blueprint, request, jsonify, send_file
from backend.app.services import rmq_producer, cache_service
import uuid
import hashlib
import os

search_bp = Blueprint('search_bp', __name__)


@search_bp.route('/search', methods=['POST'])
def initiate_search():
    data = request.get_json()
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    # 1. Проверяем кэш по MD5-хешу запроса
    query_hash = hashlib.md5(query.encode()).hexdigest()
    cached_result = cache_service.get_from_cache(query_hash)

    if cached_result:
        # Возвращаем кэшированный результат
        return jsonify({
            'task_id': cached_result['task_id'],
            'cached': True,
            'result': cached_result['result']
        })

    # 2. Нет в кэше — создаём новую задачу
    task_id = str(uuid.uuid4())

    # Устанавливаем начальный статус задачи
    cache_service.set_status(task_id, 'pending')

    # 3. Помещаем задачу в очередь RabbitMQ
    rmq_producer.send_task(task_id, query)

    return jsonify({'task_id': task_id}), 202


@search_bp.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    status, result = cache_service.get_task_result(task_id)

    if status == 'not_found':
        return jsonify({'error': 'Task not found'}), 404

    return jsonify({'status': status, 'result': result})


@search_bp.route('/download/<task_id>', methods=['GET'])
def download_excel(task_id):
    file_path = cache_service.get_excel_file_path(task_id)

    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(file_path, as_attachment=True, download_name=f'report_{task_id}.xlsx')
