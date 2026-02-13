"""
Клиент для OpenRouter API.
Поддерживает извлечение JSON из ответов LLM.
"""

import json
import os
import re
from typing import Optional, Dict, Any, List

import requests
from dotenv import load_dotenv

load_dotenv()


class OpenRouterClient:
    """
    Клиент для работы с OpenRouter API.
    Поддерживает различные модели (Qwen, Llama, etc.)
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    # Рекомендуемые модели для извлечения структурированных данных
    RECOMMENDED_MODELS = {
        "qwen": "qwen/qwen-2.5-7b-instruct",  # Дешёвая, хорошая для JSON
        "llama": "meta-llama/llama-3.1-8b-instruct",  # Баланс цена/качество
        "gemma": "google/gemma-2-9b-it",  # Компактная
        "deepseek": "deepseek/deepseek-chat",  # Лучшая для русского
    }

    def __init__(
            self,
            api_key: Optional[str] = None,
            model: Optional[str] = None,
            temperature: float = 0.1,
            max_tokens: int = 512
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY не задан. Установите переменную окружения.")

        self.model = model or os.getenv("OPENROUTER_MODEL", self.RECOMMENDED_MODELS["qwen"])
        self.temperature = temperature
        self.max_tokens = max_tokens

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://hydro-search.local",  # Требуется OpenRouter
            "X-Title": "Hydro RAG Search"
        })

        print(f"OpenRouter клиент инициализирован: {self.model}")

    def generate(
            self,
            system_prompt: str,
            user_prompt: str,
            temperature: Optional[float] = None
    ) -> str:
        """
        Генерация текста через OpenRouter.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": self.max_tokens
        }

        try:
            response = self.session.post(
                f"{self.BASE_URL}/chat/completions",
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ошибка OpenRouter API: {e}")

    def extract_json(
            self,
            system_prompt: str,
            user_prompt: str,
            temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Генерация с извлечением JSON из ответа.
        """
        content = self.generate(system_prompt, user_prompt, temperature)
        return self._parse_json_from_text(content)

    def _parse_json_from_text(self, text: str) -> Dict[str, Any]:
        """
        Извлечение JSON из текста ответа LLM.
        """
        # Удаляем markdown-обёртки если есть
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        # Ищем JSON объект
        patterns = [
            r'\{[^{}]*\}',  # Простой объект
            r'\{[^{}]*\{[^{}]*\}[^{}]*\}',  # Вложенный (1 уровень)
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue

        # Fallback: пустой объект
        return {}

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Получение статистики использования (требуется ключ с правами).
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/credits")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "Нет доступа к статистике"}

    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        Список доступных моделей.
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/models")
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения списка моделей: {e}")
            return []