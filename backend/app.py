from flask import Flask
from flask_cors import CORS

#sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from routes.api import bp as api_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_pyfile('config.py')
    app.register_blueprint(api_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
