# hydro_find/models/ai_models.py

import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_OPEN_ROUTER")
GEMMA_3_27B_IT = os.getenv("GEMMA_3_27B_IT")


AVAILABLE_MODELS = {
   #to do
}

DEFAULT_MODEL = GEMMA_3_27B_IT



def get_api_key() -> str:
    if not API_KEY or API_KEY.startswith("sk-or-v1-"):
        return API_KEY
    raise ValueError("OPENROUTER_API_KEY не настроен")


def get_default_model() -> str:
    return DEFAULT_MODEL


def get_available_models() -> Dict[str, str]:
    return AVAILABLE_MODELS