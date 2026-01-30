# backend/services/ai_service.py

from backend.ai.service import AIProcessingService

class AIService:
    def __init__(self):
        self._ai = AIProcessingService()

    def process_single(self, query: str) -> dict:
        return self._ai.process_single(query)

    def process_batch(self, text: str) -> dict:
        return self._ai.process_batch(text)

    def parse_and_process_text(self, full_text: str) -> list[dict]:
        # to do
        pass