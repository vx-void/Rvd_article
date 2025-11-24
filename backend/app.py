from flask import Flask, render_template
from flask_cors import CORS
import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.routes.api import bp as api_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_pyfile('../config.py')

    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=80)