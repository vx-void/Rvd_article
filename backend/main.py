import os
from urllib.parse import quote_plus

import config
from flask import Flask
from flask_cors import CORS

from config import Config

# API
from core.api.search_blueprint import create_search_blueprint

# Application layer
from core.application.search_service import SearchService
from core.application.task_service import TaskService

# Messaging
from core.messaging.producer import RabbitMQProducer

# Database
from database.connection import DatabaseConnection
from database.repository.sqlalchemy_repository import SqlAlchemyComponentRepository


def create_app(config_class: type[Config] = Config) -> Flask:
    """
    Фабрика веб-приложения.
    """

    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)

    # -------------------------
    # Инициализация инфраструктуры
    # -------------------------


    db_connection = DatabaseConnection(
        database_url=app.config["DATABASE_URL"]
    )
    session = db_connection.get_session()

    repository = SqlAlchemyComponentRepository(session)

    producer = RabbitMQProducer(
        host=app.config["RABBITMQ_HOST"],
        queue_name=app.config["RABBITMQ_QUEUE"]
    )

    task_service = TaskService(repository=repository)

    search_service = SearchService(
        producer=producer,
        task_service=task_service
    )

    # -------------------------
    # Создание Blueprint через фабрику
    # -------------------------

    search_bp = create_search_blueprint(search_service)

    app.register_blueprint(search_bp)

    # -------------------------
    # Обработчики ошибок
    # -------------------------

    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=app.config.get("PORT", 5000)
    )
