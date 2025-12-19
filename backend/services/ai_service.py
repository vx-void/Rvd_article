from hydro_find.ai import AIProcessingService

class AIService:
    def __init__(self):
        self._ai = AIProcessingService()

    def process_user_input(self, text: str) -> dict:
        # Автоматическое определение: пакетный или одиночный?
        if '\n' in text or (' - ' in text and text.count(' - ') > 1):
            return self._ai.process_batch(text)
        else:
            return self._ai.process_single(text)