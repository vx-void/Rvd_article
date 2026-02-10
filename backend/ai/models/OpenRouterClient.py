#../ai/OpenRouterClient.py

import json
import logging
from typing import Optional, Dict, Any
from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from dotenv import load_dotenv
from ai.interfaces.ai_client import IAIClient


logger = logging.getLogger(__name__)

load_dotenv()

class OpenRouterClient(IAIClient):

    def __init__(self):
        self.api_key = self._get_api_key()
        self.model = self._get_default_model()
        self.timeout = self._get_timeout()

        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            timeout=self.timeout,
            temperature=0.2,
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

    def _get_api_key() -> str:
        return os.getenv("API_OPEN_ROUTER")
    
    def _get_default_model() -> str:
        return os.getenv("GEMMA_3_27B_IT")
    
    def _get_timeout() -> int:  # TO DO
        return 120
    


    if __name__ == "__main__":
        openRouter = OpenRouterClient()
        print = openRouter.generate("проверка связи", "Ghbdtn")