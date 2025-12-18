# hydro_find/ai/openrouter_client.py

import json
from typing import Optional, Dict, Any
from openai import OpenAI
from hydro_find.ai.models.ai_models import get_api_key, get_default_model
from hydro_find.ai.prompts.classification_prompt import CLASSIFICATION_PROMPT


class OpenRouterClient:
    """Клиент для работы с OpenRouter API."""

    def __init__(self):
        self.api_key = get_api_key()
        self.model = get_default_model()
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "http://localhost",
                "X-Title": "Hydro-Search APP"
            }
        )

    def generate_response(
        self,
        system_prompt: str,
        user_query: str,
        temperature: float = 0.2,
        timeout: int = 120
    ) -> Optional[str]:
        """Выполняет запрос к модели и возвращает текстовый ответ."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=temperature,
                timeout=timeout
            )
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[ERROR] OpenRouterClient.generate_response: {e}")
        return None


class ComponentClassifier:
    """Классификатор типа гидравлического компонента."""

    def __init__(self):
        self.client = OpenRouterClient()

    def classify(self, query: str) -> Optional[str]:
        """Возвращает строку: 'fittings', 'adapters', и т.д."""
        response = self.client.generate_response(CLASSIFICATION_PROMPT, query)
        if response:
            return response.lower().strip().strip('"\'')
        return None


class ComponentModel:
    """Модель для извлечения структурированных параметров по промпту."""

    def __init__(self, system_prompt: str):
        self.client = OpenRouterClient()
        self.system_prompt = system_prompt

    def extract_json(self, query: str) -> Optional[Dict[str, Any]]:
        """Извлекает JSON или возвращает {'raw_response': ...}."""
        response = self.client.generate_response(self.system_prompt, query)
        if not response:
            return None

        try:
            if response.strip().startswith('{') and response.strip().endswith('}'):
                return json.loads(response)
        except json.JSONDecodeError:
            pass

        return {"raw_response": response}