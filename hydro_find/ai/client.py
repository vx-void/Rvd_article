# hydro_find/ai/client.py

import json
from typing import Optional, Dict, Any
from openai import OpenAI
from hydro_find.ai.models.ai_models import get_api_key, get_default_model

class OpenRouterClient:
    def __init__(self):
        self.api_key = get_api_key()
        self.model = get_default_model()
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "http://localhost",
                "X-Title": "Hydro-Search APP"
            }
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
                timeout=120
            )
            return response.choices[0].message.content.strip() if response.choices else None
        except Exception as e:
            print(f"[AI Client Error] {e}")
            return None

    def extract_json(self, system_prompt: str, user_query: str) -> Optional[Dict[str, Any]]:
        text = self.generate(system_prompt, user_query)
        if not text:
            return None
        try:
            if text.strip().startswith('{') and text.strip().endswith('}'):
                return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        return {"raw_response": text}