# hydro_find/ai/openrouter_client.py

import json
from typing import Optional, Dict, Any
from openai import OpenAI
from hydro_find.ai.models.ai_models import get_api_key, get_default_model


class OpenRouterClient:
    """Клиент для безопасного взаимодействия с OpenRouter API."""

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
        """Выполняет запрос к модели и возвращает чистый текстовый ответ."""
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
    """Классификатор типа компонента (возвращает строку: 'fittings', 'adapters', и т.д.)."""

    def __init__(self):
        self.client = OpenRouterClient()

    def classify(self, query: str) -> Optional[str]:
        """Возвращает нормализованную строку типа компонента или None."""
        from hydro_find.prompts import get_preprocessing_prompt
        # Используем промпт классификации (он возвращает plain text, не JSON)
        classification_prompt = get_preprocessing_prompt("classify")  # ← нужно добавить!
        response = self.client.generate_response(classification_prompt, query)
        if response:
            raw = response.lower().strip().strip('"\'')
            # Поддерживаем только известные типы
            allowed = {"fittings", "adapters", "plugs", "adapter-tee", "banjo", "banjo-bolt", "brs", "coupling"}
            return raw if raw in allowed else None
        return None


class ComponentModel:
    """Модель для извлечения структурированных данных по заданному промпту."""

    def __init__(self, system_prompt: str):
        self.client = OpenRouterClient()
        self.system_prompt = system_prompt  # ← сохраняем для использования в extract_json

    def extract_json(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Запрашивает у модели JSON и пытается его распарсить.
        При ошибке возвращает {"raw_response": ...}.
        """
        response_text = self.client.generate_response(self.system_prompt, query)
        if not response_text:
            return None

        try:
            # Проверяем, что строка похожа на JSON
            stripped = response_text.strip()
            if stripped.startswith('{') and stripped.endswith('}'):
                return json.loads(stripped)
        except json.JSONDecodeError:
            pass

        # Fallback: возвращаем как есть
        return {"raw_response": response_text}