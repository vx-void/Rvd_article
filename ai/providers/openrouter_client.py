import json
import os
from typing import Optional, Any, Dict
from openai import OpenAI
from dotenv import load_dotenv

from ai.models.types import ComponentType

load_dotenv()

class OpenRouterClient:
    def __init__(self, model: Optional[str] = None):
        self.api_key = os.getenv('API_OPEN_ROUTER')
        self.base_url = os.getenv('OPEN_ROUTER')
        self.model = model or os.getenv('GEMMA_3_27B_IT')

        if not self.api_key or not self.base_url:
            raise ValueError("API ключ или URL OpenRouter не настроены")

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
        """
        Args:
            system_prompt: Системный промпт
            user_query: Пользовательский запрос
            temperature: Температура генерации
            timeout: Таймаут запроса

        Returns:
            Ответ от модели или None при ошибке
        """
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
            print(f"Ошибка при генерации ответа: {e}")

        return None


class ComponentModel:
    def __init__(self, system_prompt: str):
        self.client = OpenRouterClient()
        self.system_prompt = system_prompt

    def extract_data(self, query: str) -> Optional[str]:
        """
        Args:
            query: Пользовательский запрос

        Returns:
            Извлеченные данные в виде строки
        """
        return self.client.generate_response(self.system_prompt, query)

    def extract_json(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Args:
            query: Пользовательский запрос

        Returns:
            Данные в формате словаря или None при ошибке
        """
        response = self.extract_data(query)
        if not response:
            return None

        try:
            # Пробуем распарсить JSON
            if response.strip().startswith('{') and response.strip().endswith('}'):
                return json.loads(response)
        except json.JSONDecodeError:
            pass

        return {"raw_response": response}


class ComponentClassifier:
    def __init__(self):
        self.client = OpenRouterClient()

    def classify(self, query: str) -> Optional[ComponentType]:
        """
        Args:
            query: Пользовательский запрос

        Returns:
            Тип компонента или None при ошибке
        """
        from ai.promts.classification_prompt import CLASSIFICATION_PROMPT

        response = self.client.generate_response(
            system_prompt=CLASSIFICATION_PROMPT,
            user_query=query
        )

        if response:
            try:
                return ComponentType(response.lower().strip())
            except ValueError:
                print(f"Неизвестный тип компонента: {response}")

        return None