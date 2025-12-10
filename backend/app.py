from flask import Flask, send_from_directory, render_template, jsonify
from flask_cors import CORS
import requests
import sys
import os

#sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from routes.api import bp as api_bp



EXAMPLE = {
    "фитинг": [
        {"type": "fitting", "text": "FIT-12345", "description": "Фитинг гидравлический 3/4\""},
        {"type": "fitting", "text": "FIT-67890", "description": "Фитинг нержавеющий 1/2\""}
    ],
    "адаптер": [
        {"type": "adapter", "text": "ADP-101", "description": "Адаптер переходной стальной"}
    ]
}



def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_pyfile('config.py')
    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        pass
    return app


    @app.route('/api/process-query', methods=['POST'])
    def process_query():
        pass



    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "hydropoisk-api",
            "version": "1.0.0"
        })

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=80)
