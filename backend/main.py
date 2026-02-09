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
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)

    # --- Database ---
    db_connection = DatabaseConnection(
        database_url=app.config["DATABASE_URL"]
    )
    session = db_connection.get_session()
    repository = SqlAlchemyComponentRepository(session)

    # --- Messaging ---
    producer = RabbitMQProducer(
        host=app.config["RABBITMQ_HOST"],
        queue_name=app.config["RABBITMQ_QUEUE"],
        username=app.config.get("RABBITMQ_USER"),
        password=app.config.get("RABBITMQ_PASS"),
    )
    producer.connect()  # критически важно

    # --- Application services ---
    task_service = TaskService(repository=repository)

    search_service = SearchService(
        task_service=task_service,
        message_broker=producer
    )

    # --- API ---
    search_bp = create_search_blueprint(search_service)
    app.register_blueprint(search_bp)

    return app


# Глобальный объект для flask run
app = create_app()


if __name__ == "__main__":
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.methods} -> {rule}")


    @app.route("/ping")
    def ping():
        return {"status": "ok"}

    app.run(
        host="0.0.0.0",
        port=app.config.get("PORT", 5000),
        debug=True
    )
