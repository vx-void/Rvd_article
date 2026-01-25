# backend/app/__init__.py

from flask import Flask
from flask_cors import CORS
import logging
import os

# Импортируем blueprint из правильного места
from backend.app.api.search_blueprint import search_bp

# Инициализация логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class App:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(App, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_class=None, testing=False):
        if App._initialized and not testing:
            return

        self.app = Flask(__name__)
        self.testing = testing

        self._configure_app(config_class)
        self._initialize_middleware()
        self._register_blueprints()
        self._register_error_handlers()

        App._initialized = True
        logger.info("FlaskApp initialized")

    def _configure_app(self, config_class):
        from backend.app.config import Config, DevelopmentConfig, ProductionConfig

        if config_class:
            self.app.config.from_object(config_class)
        else:
            env = os.getenv('FLASK_ENV', 'development')
            if env == 'production':
                self.app.config.from_object(ProductionConfig)
            elif env == 'testing':
                self.app.config.from_object(Config)
                self.app.config['TESTING'] = True
            else:
                self.app.config.from_object(DevelopmentConfig)

        self.app.config.update({
            'JSON_SORT_KEYS': False,
            'JSONIFY_PRETTYPRINT_REGULAR': True,
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
        })

        self.app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    def _initialize_middleware(self):
        CORS(self.app,
             resources={r"/api/*": {"origins": "*"}},
             supports_credentials=True)

    def _register_blueprints(self):
        # Регистрация blueprint с префиксом /api
        # ВАЖНО: используем app.api.search_blueprint
        self.app.register_blueprint(search_bp, url_prefix='/api')

    def _register_error_handlers(self):
        @self.app.errorhandler(404)
        def not_found_error(error):
            return {"success": False, "error": {"message": "Resource not found"}}, 404

        @self.app.errorhandler(500)
        def internal_error(error):
            return {"success": False, "error": {"message": "Internal server error"}}, 500

    def get_app(self):
        return self.app

    def run(self, host='0.0.0.0', port=5000, debug=None, **options):
        if debug is None:
            debug = self.app.config.get('DEBUG', False)

        logger.info(f"Starting HydroFind API on http://{host}:{port}")
        logger.info(f"Environment: {self.app.config.get('ENV', 'production')}")
        logger.info(f"Debug mode: {debug}")

        # Вывод зарегистрированных маршрутов
        with self.app.app_context():
            logger.info("=== Registered routes ===")
            for rule in self.app.url_map.iter_rules():
                methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
                logger.info(f"{rule.endpoint:30} [{methods}] → {rule.rule}")
            logger.info("=========================")

        self.app.run(
            host=host,
            port=port,
            debug=debug,
            **options
        )

    @property
    def config(self):
        return dict(self.app.config)


def create_app(config_class=None, testing=False):

    flask_app_instance = App(config_class=config_class, testing=testing)
    return flask_app_instance.get_app()


if __name__ == '__main__':
    # Создаём и запускаем приложение
    app_instance = App()
    app = app_instance.get_app() # Получаем объект Flask
    app_instance.run() # Запускаем с настройками инстанса
