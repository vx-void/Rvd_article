# backend/app/api/search_blueprint.py

from flask import Blueprint, request, jsonify, send_file
from backend.app.services import rmq_producer
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


    # 2. Нет в кэше — создаём новую задачу
    task_id = str(uuid.uuid4())

    # Устанавливаем начальный статус задачи

    # 3. Помещаем задачу в очередь RabbitMQ
    rmq_producer.send_task(task_id, query)

    return jsonify({'task_id': task_id}), 202



