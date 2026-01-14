import json
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from openai._exceptions import APIConnectionError, APIError, RateLimitError
from hydro_find.ai.models.ai_models import get_api_key, get_default_model, get_timeout

logger = logging.getLogger(__name__)


class OpenRouterClient:
    def __init__(self):
        self.api_key = get_api_key()
        self.model = get_default_model()
        self.timeout = get_timeout()

        try:
            self._client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
                max_retries=3,
                timeout=self.timeout,
                default_headers={
                    "HTTP-Referer": "http://localhost:3000",  # Исправленный заголовок
                    "X-Title": "Hydro-Search APP"
                }
            )
            logger.info(f"OpenRouter клиент инициализирован с моделью: {self.model}")
        except Exception as e:
            logger.error(f"Ошибка инициализации OpenRouter клиента: {e}")
            raise

    def generate(self, system_prompt: str, user_query: str) -> Optional[str]:
        """Генерация ответа от AI"""
        try:
            logger.debug(f"Отправка запроса к AI. Модель: {self.model}")

            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.2,
                timeout=self.timeout,
                max_tokens=2000
            )

            if response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content.strip()
                logger.debug(f"Получен ответ от AI, длина: {len(content)} символов")
                return content
            else:
                logger.warning("AI вернул пустой ответ")
                return None

        except APIConnectionError as e:
            logger.error(f"Ошибка подключения к OpenRouter API: {e}")
            return None
        except RateLimitError as e:
            logger.error(f"Превышен лимит запросов к OpenRouter: {e}")
            return None
        except APIError as e:
            logger.error(f"Ошибка API OpenRouter: {e}")
            return None
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при запросе к AI: {e}")
            return None

    def extract_json(self, system_prompt: str, user_query: str) -> Optional[Dict[str, Any]]:
        """Извлечение JSON из ответа AI"""
        logger.debug("Извлечение JSON из ответа AI")

        text = self.generate(system_prompt, user_query)
        if not text:
            logger.warning("Не удалось получить ответ от AI для извлечения JSON")
            return None

        try:
            # Пытаемся найти JSON в тексте
            text = text.strip()

            # Ищем начало и конец JSON
            start_idx = text.find('{')
            end_idx = text.rfind('}')

            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx + 1]
                result = json.loads(json_str)
                logger.debug(f"JSON успешно извлечен, ключи: {list(result.keys())}")
                return result
            else:
                # Если нет JSON, возвращаем raw текст
                logger.warning(f"AI не вернул JSON. Ответ: {text[:100]}...")
                return {"raw_response": text}

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}. Текст: {text[:200]}...")
            return {"raw_response": text}
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при извлечении JSON: {e}")
            return {"raw_response": text}