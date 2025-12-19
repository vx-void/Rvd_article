# hydro_find/models/ai_models.py

import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

def get_api_key() -> str:
    """Возвращает API-ключ OpenRouter из переменной окружения."""
    key = os.getenv("API_OPEN_ROUTER")
    if not key:
        raise ValueError("Переменная API_OPEN_ROUTER не задана в .env")
    return key

def get_default_model() -> str:
    """Возвращает модель по умолчанию (Gemma 3 27B)."""
    return "google/gemma-3-27b-it:free"