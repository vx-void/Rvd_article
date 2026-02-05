#../ai/interfaces/ai_client.py

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class AIClientInterface(ABC):

    @abstractmethod
    def generate(self, system_prompt: str, user_query: str) -> Optional[str]:
        pass

    @abstractmethod
    def extract_json(
        self, system_prompt: str, user_query: str
    ) -> Optional[Dict[str, Any]]:
        pass
