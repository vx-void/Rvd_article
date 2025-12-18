from hydro_find.ai.ai_service import AIProcessingService

class AIService:
    def __init__(self):
        self._ai = AIProcessingService()

    def handle_user_input(self, text: str) -> dict:
        # Автоматически определяем: пакетный или одиночный?
        if '\n' in text or ' - ' in text and text.count(' - ') > 1:
            return self._ai.process_batch_query(text)
        else:
            return self._ai.process_query(text)