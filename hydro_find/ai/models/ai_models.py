import os
import logging
from dotenv import load_dotenv
from pathlib import Path

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


def get_max_tokens() -> int:
    """Возвращает максимальное количество токенов."""
    max_tokens = os.getenv("AI_MAX_TOKENS", "2000")
    try:
        return int(max_tokens)
    except ValueError:
        logger.warning(f"Некорректное количество токенов: {max_tokens}, использую 2000")
        return 2000


def check_api_key() -> bool:
    """Проверка доступности API ключа."""
    try:
        key = get_api_key()
        if key and len(key) > 10:
            logger.info("API ключ загружен успешно")
            return True
        return False
    except ValueError:
        return False


def get_available_models() -> list:
    """Возвращает список доступных моделей."""
    return [
        # Бесплатные модели
        "google/gemma-2-27b-it:free",
        "google/gemma-3-27b-it:free",
        "meta-llama/llama-3.1-8b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        # Платные модели (если есть премиум ключ)
        "openai/gpt-4o-mini",
        "anthropic/claude-3-haiku",
        "meta-llama/llama-3.1-70b-instruct",
    ]