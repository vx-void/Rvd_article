from flask import Blueprint, request, jsonify
from backend.services.ai_service import process_component_query
import uuid
import json
import redis

bp = Blueprint('api', __name__, url_prefix='/api')

# Redis-клиент (в реальном проекте — через Dependency Injection)
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

@bp.route('/v1/search', methods=['POST'])
def search_articles():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({"error": "Поле 'text' обязательно"}), 400

    request_id = str(uuid.uuid4())
    # Публикация в RabbitMQ будет здесь (заглушка)
    # В этом примере — синхронная обработка
    result = process_component_query(text)
    if result["success"]:
        redis_client.setex(f"result:{request_id}", 3600, json.dumps(result))
        return jsonify({"request_id": request_id, "status": "processing"}), 202
    else:
        return jsonify(result), 400

@bp.route('/v1/result/<request_id>', methods=['GET'])
def get_result(request_id):
    data = redis_client.get(f"result:{request_id}")
    if data:
        return jsonify(json.loads(data))
    return jsonify({"error": "Результат не найден или устарел"}), 404