import os
from dotenv import load_dotenv

load_dotenv()  # Загрузка переменных окружения из .env


class Config:
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # Redis
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = 6379

    # RabbitMQ
    RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST')
    RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT')
    RABBITMQ_USER = os.environ.get('RABBITMQ_USER')
    RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS')


    # OpenRouter
    API_OPEN_ROUTER = os.environ.get('API_OPEN_ROUTER')

    # Supabase config
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SUPABASE_HOST = os.environ.get('SUPABASE_HOST')
    SUPABASE_DATABASE = os.environ.get('SUPABASE_DATABASE')
    SUPABASE_USER = os.environ.get('SUPABASE_USER')
    SUPABASE_PASSWORD = os.environ.get('SUPABASE_PASSWORD')
    SUPABASE_PORT = os.environ.get('SUPABASE_PORT')


class DevelopmentConfig(Config):
    """Конфигурация для разработки."""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    """Конфигурация для продакшена."""
    DEBUG = False
    ENV = 'production'


