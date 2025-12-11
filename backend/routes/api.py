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
   pass


@bp.route('/excel', methods=['GET'])
def excel_download():
    pass

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'Backend alive',
        'client_ip': request.remote_addr,
        'user_aget':str(request.user_agent),
        'timestamp': datetime.now().isoformat()
    })

