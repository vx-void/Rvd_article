from flask import Blueprint, request, jsonify
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    #from hydro_find.ai.classifiers import classificator
    from backend.services.ai_service import process_component_query

    AI_AVAILABLE = True
except ImportError as e:
    print(f"AI module not available: {e}")
    AI_AVAILABLE = False

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/process-query', methods=['POST'])
def process_query():
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({'error': 'Сообщение отсутствует'}), 400

        user_message = data['message']
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"[{timestamp}] Получен запрос: '{user_message}'")

        if AI_AVAILABLE:
            try:
                result = process_component_query(user_message)
                return jsonify({
                    'status': 'success',
                    'results': result,
                    'timestamp': timestamp,
                    'source': 'ai'
                })
            except Exception as ai_error:
                print(f"[ERROR] AI processing failed: {str(ai_error)}")
                return get_demo_response(user_message, timestamp)
        else:
            return get_demo_response(user_message, timestamp)

    except Exception as e:
        print(f"[ERROR] Ошибка при обработке запроса: {str(e)}")
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500


@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'ai_available': AI_AVAILABLE,
        'timestamp': datetime.now().isoformat()
    })


def get_demo_response(user_message, timestamp):
    demo_results = [
        {"name": "Фитинг DKOL 12x1.5", "article": "ART-001", "type": "fitting"},
        {"name": "Адаптер BSP 1\" (Г-Г)", "article": "ART-002", "type": "adapter"},
        {"name": "Заглушка BSP 1\"", "article": "ART-003", "type": "plug"}
    ]

    return jsonify({
        'status': 'success',
        'results': demo_results,
        'timestamp': timestamp,
        'source': 'demo'
    })