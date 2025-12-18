from hydro_find.ai.ai_service import AIProcessingService

class AIService:
    def __init__(self):
        self._ai = AIProcessingService()

    def process_user_query(self, query: str) -> dict:
        return self._ai.process_query(query)