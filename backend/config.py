import os
from dotenv import load_dotenv

load_dotenv()  # Загрузка переменных окружения из .env


class Config:
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # Redis
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

    # RabbitMQ
    RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))

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

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    CRYPTO_SECRET_KEY = os.environ.get('CRYPTO_SECRET_KEY')

    # Application
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = os.environ.get('TESTING', 'False').lower() == 'true'

    # Password Policies
    MIN_PASSWORD_LENGTH = int(os.environ.get('MIN_PASSWORD_LENGTH', 8))
    REQUIRE_PASSWORD_COMPLEXITY = os.environ.get('REQUIRE_PASSWORD_COMPLEXITY', 'True').lower() == 'true'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False