# backend/services/ai_service.py

from hydro_find.ai.service import AIProcessingService

class AIService:
    def __init__(self):
        self._ai = AIProcessingService()

    def process_single(self, query: str) -> dict:
        return self._ai.process_single(query)

    def process_batch(self, text: str) -> dict:
        return self._ai.process_batch(text)