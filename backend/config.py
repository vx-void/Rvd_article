import os
from dotenv import load_dotenv

load_dotenv()  # Загрузка переменных окружения из .env

class Config:
    # Database

    PG_USER = os.getenv("PG_USER")
    PG_PASSWORD = os.getenv("PG_PASSWORD")
    PG_HOST = os.getenv("PG_HOST")
    PG_PORT = os.getenv("PG_PORT")
    PG_DATABASE = os.getenv("PG_DATABASE")

    DATABASE_URL = os.getenv('DATABASE_URL')

    # RabbitMQ
    RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST')
    RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT')
    RABBITMQ_USER = os.environ.get('RABBITMQ_USER')
    RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS')
    RABBITMQ_VHOST = os.environ.get('RABBITMQ_VHOST')

    RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")

    # OpenRouter
    API_OPEN_ROUTER = os.environ.get('API_OPEN_ROUTER')


class DevelopmentConfig(Config):
    """Конфигурация для разработки."""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    """Конфигурация для продакшена."""
    DEBUG = False
    ENV = 'production'


