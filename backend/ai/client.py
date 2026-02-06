#../ai/client.py

import json
import logging
from typing import Optional, Dict, Any
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

from backend.ai.interfaces.ai_client import AIClientInterface
from backend.ai.models import get_api_key, get_default_model, get_timeout

logger = logging.getLogger(__name__)


class OpenRouterClient(AIClientInterface):

    def __init__(self):
        self.api_key = get_api_key()
        self.model = get_default_model()
        self.timeout = get_timeout()

        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            timeout=self.timeout,
            max_retries=3
        )

    def generate(self, system_prompt: str, user_query: str) -> Optional[str]:
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            return response.choices[0].message.content.strip()
        except (APIError, APIConnectionError, RateLimitError) as e:
            logger.error(f"AI error: {e}")
            return None

    def extract_json(
        self, system_prompt: str, user_query: str
    ) -> Optional[Dict[str, Any]]:
        text = self.generate(system_prompt, user_query)
        if not text:
            return None

        try:
            start = text.find("{")
            end = text.rfind("}")
            return json.loads(text[start:end + 1])
        except Exception:
            return None
