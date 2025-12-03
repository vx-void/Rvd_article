from flask import Flask, send_from_directory, render_template
from flask_cors import CORS
import sys
import os

#sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.routes.api import bp as api_bp


# Моковые данные для примера
MOCK_DATABASE = {
    "фитинг": [
        {"type": "fitting", "text": "FIT-12345", "description": "Фитинг гидравлический 3/4\""},
        {"type": "fitting", "text": "FIT-67890", "description": "Фитинг нержавеющий 1/2\""}
    ],
    "шланг": [
        {"type": "hose", "text": "HOSE-456", "description": "Шланг высокого давления DN20"},
        {"type": "hose", "text": "HOSE-789", "description": "Шланг резиновый армированный"}
    ],
    "адаптер": [
        {"type": "adapter", "text": "ADP-101", "description": "Адаптер переходной стальной"}
    ]
}



def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_pyfile('core\\config.py')
    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
       #return render_template('..\\fronten\\index.html')
       return send_from_directory(os.path.join(app.root_path,'..', 'templates'), 'index.html')
    return app


    @app.route('/api/process-query', methods=['POST'])
    def process_query():
        """Основной endpoint для обработки запросов"""
        try:
            data = request.get_json()
            if not data or 'message' not in data:
                return jsonify({"error": "No query provided"}), 400

            query = data['message'].lower().strip()
            print(f"Получен запрос: {query}")

        # Простая логика поиска
            results = []
            for keyword, items in MOCK_DATABASE.items():
                if keyword in query:
                    results.extend(items)

        # Если ничего не найдено, возвращаем демо-данные
                if not results:
                    results = [
                    {"type": "demo", "text": "DEMO-001", "description": "Демонстрационный компонент 1"},
                    {"type": "demo", "text": "DEMO-002", "description": "Демонстрационный компонент 2"}
                    ]

            return jsonify({
                "status": "success",
                "query": query,
                "results": results,
                "count": len(results)
                })

        except Exception as e:
            print(f"Ошибка: {e}")
            return jsonify({"error": str(e)}), 500


    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Проверка работоспособности API"""
        return jsonify({
            "status": "healthy",
            "service": "hydropoisk-api",
            "version": "1.0.0"
        })

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=80)