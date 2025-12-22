from flask import Flask
from flask_cors import CORS

from .routes.search import search_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_pyfile('config.py')
    app.register_blueprint(search_bp, url_prefix='/api')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
