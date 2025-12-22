# backend/routes/search.py

from flask import Blueprint, request, jsonify
from ..services.ai_service import AIService
from ..services.db_service import DBService
from ..utils.responses import success_response, error_response

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['POST'])
def search_components():
    data = request.get_json()
    user_query = data.get('query', '')

    if not user_query:
        return error_response("Параметр 'query' обязателен", 400)

    # 1. Обработка ИИ
    ai_service = AIService()
    ai_result = ai_service.process_single(user_query)

    if not ai_result["success"]:
        return error_response(ai_result["error"], 500)

    # 2. Поиск в БД по ИИ-параметрам
    db_service = DBService()
    matches = db_service.search_by_ai_params({
        "component_type": ai_result["component_type"],
        "original_query": user_query,
        **ai_result["extracted_data"]
    })

    # 3. Формирование ответа
    if matches:
        return success_response({
            "source": "database",
            "matches": matches,
            "ai_result": ai_result
        })

    # Если в БД нет — возвращаем только ИИ-результат
    return success_response({
        "source": "ai_only",
        "ai_result": ai_result
    })