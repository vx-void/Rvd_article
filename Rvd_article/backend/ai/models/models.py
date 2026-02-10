import os
import logging
from dotenv import load_dotenv


logger = logging.getLogger(__name__)

# Загружаем переменные из .env

load_dotenv()

def get_api_key() -> str:
        return os.getenv("API_OPEN_ROUTER")

def get_default_model() -> str:
    return os.getenv("GEMMA_3_27B_IT")


def get_timeout() -> int:
    """Возвращает таймаут для запросов."""
    timeout = os.getenv("AI_TIMEOUT", "120")
    try:
        return int(timeout)
    except ValueError:
        logger.warning(f"Некорректный таймаут: {timeout}, использую 120 секунд")
        return 120


