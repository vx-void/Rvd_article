from flask import Flask
from flask_cors import CORS
from .routes.search import search_bp
import logging
import os

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
        from .config import Config, DevelopmentConfig, ProductionConfig

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

        # Дополнительные настройки
        self.app.config.update({
            'JSON_SORT_KEYS': False,
            'JSONIFY_PRETTYPRINT_REGULAR': True,
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
        })

        # Секретный ключ
        self.app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

    def _initialize_middleware(self):
        CORS(self.app,
             resources={r"/api/*": {"origins": "*"}},
             supports_credentials=True)

    def _register_blueprints(self):
        # Регистрация blueprint с префиксом /api — ТОЛЬКО ЗДЕСЬ!
        self.app.register_blueprint(search_bp, url_prefix='/api')

        @self.app.route('/health')
        def health_check():
            from .utils.responses import SuccessResponse
            response = SuccessResponse({"status": "healthy", "service": "hydro-find"})
            return response.to_response()

    def _register_error_handlers(self):
        @self.app.errorhandler(404)
        def not_found_error(error):
            from .utils.responses import ErrorResponse
            response = ErrorResponse("Resource not found", 404)
            return response.to_response()

        @self.app.errorhandler(500)
        def internal_error(error):
            from .utils.responses import ErrorResponse
            response = ErrorResponse("Internal server error", 500)
            return response.to_response()

    def get_app(self):
        return self.app

    def run(self, host='0.0.0.0', port=5000, debug=None, **options):
        if debug is None:
            debug = self.app.config.get('DEBUG', False)

        logger.info(f"Starting HydroFind API on http://{host}:{port}")
        logger.info(f"Environment: {self.app.config.get('ENV', 'production')}")
        logger.info(f"Debug mode: {debug}")

        # === ОПЦИОНАЛЬНО: вывод всех маршрутов для диагностики ===
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

    def create_test_client(self):
        """Создание тестового клиента"""
        self.app.config['TESTING'] = True
        return self.app.test_client()

    @property
    def config(self):
        return dict(self.app.config)


def create_app(config_class=None, testing=False):
    flask_app = App(config_class=config_class, testing=testing)
    return flask_app.get_app()


if __name__ == '__main__':
    app = App()
    app.run()