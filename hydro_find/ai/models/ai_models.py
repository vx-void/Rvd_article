# hydro_find/models/ai_models.py

import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()
# 🔑 OpenRouter API-ключ (лучше брать из .env, но можно и хардкодить временно)
API_KEY = os.getenv("API_OPEN_ROUTER")

# 🤖 Основная модель — Gemma 3 27B (бесплатная, как в вашем профиле)
GEMMA_3_27B_IT = os.getenv("GEMMA_3_27B_IT")

# 📦 Доступные модели (для расширения)
AVAILABLE_MODELS = {
   #to do
}

DEFAULT_MODEL = GEMMA_3_27B_IT


# ✅ Функции для безопасного доступа к конфигурации
def get_api_key() -> str:
    if not API_KEY or API_KEY.startswith("sk-or-v1-"):
        return API_KEY
    raise ValueError("OPENROUTER_API_KEY не настроен")


def get_default_model() -> str:
    return DEFAULT_MODEL


def get_available_models() -> Dict[str, str]:
    return AVAILABLE_MODELS