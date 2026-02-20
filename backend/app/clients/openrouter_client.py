"""OpenRouter API client with retries and circuit breaker."""

import json
import re
from typing import Any, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.app.config import get_settings
from backend.app.logging_config import get_logger


logger = get_logger("openrouter")


class OpenRouterClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.05,
        max_tokens: int = 512,
        timeout: int = 30,
    ):
        settings = get_settings()
        #self.BASE_URL = load_dotenv('OPEN_ROUTER')
        self.api_key = api_key or settings.openrouter_api_key
        self.model = model or settings.openrouter_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

        # Shared async client
        self._client: Optional[httpx.AsyncClient] = None

        logger.info(
            "openrouter_client_initialized",
            model=self.model,
            temperature=temperature,
        )

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://hydro-search.local",
                    "X-Title": "Hydro Search API",
                },
            )
        return self._client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature  = 0.1,
        max_tokens  = 300
    ) -> str:
        """Generate text with retries."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }

        client = await self._get_client()

        try:
            response = await client.post(
                f"https://openrouter.ai/api/v1/chat/completions",
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            logger.debug(
                "openrouter_request_success",
                model=self.model,
                prompt_tokens=data.get("usage", {}).get("prompt_tokens", 0),
                completion_tokens=data.get("usage", {}).get("completion_tokens", 0),
            )

            return content

        except httpx.HTTPStatusError as e:
            logger.error(
                "openrouter_http_error",
                status_code=e.response.status_code,
                response=e.response.text,
            )
            raise f"OpenRouter HTTP error: {e.response.status_code}"
        except Exception as e:
            logger.error("openrouter_error", error=str(e))
            raise f"OpenRouter error: {e}"

    async def extract_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
    ) -> dict[str, Any]:
        """Generate and parse JSON."""
        content = await self.generate(system_prompt, user_prompt, temperature)
        return self._parse_json(content)

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        """Extract JSON from LLM response."""
        text = text.strip()

        # Remove markdown fences
        for prefix in ["```json", "```"]:
            if text.startswith(prefix):
                text = text[len(prefix):]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        # Try direct parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Extract JSON object with regex
        patterns = [
            r'\{[^{}]*\}',  # Simple object
            r'\{[^{}]*\{[^{}]*\}[^{}]*\}',  # Nested one level
            r'\{.*\}',  # Greedy (last resort)
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue

        logger.warning("json_parse_failed", text=text[:200])
        return {}

    async def close(self):
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()