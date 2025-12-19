from hydro_find.ai import AIProcessingService
from .search_service import search_components_by_ai_params


class AIService:
    def __init__(self):
        self._ai = AIProcessingService()

    def process_user_input(self, text: str) -> dict:
        # Автоматическое определение: пакетный или одиночный?
        if '\n' in text or (' - ' in text and text.count(' - ') > 1):
            return self._ai.process_batch(text)
        else:
            return self._ai.process_single(text)

    def process_with_database_fallback(self, query: str) -> dict:
        ai_result = self._ai.process_single(query)
        if not ai_result["success"]:
            return ai_result

        # Поиск в БД по ИИ-параметрам
        db_matches = search_components_by_ai_params(ai_result)

        if db_matches:
            return {
                "success": True,
                "source": "database",
                "matches": db_matches,
                "ai_result": ai_result
            }

        # Если нет совпадений — возвращаем ИИ-результат как есть
        return {
            "success": True,
            "source": "ai_only",
            "ai_result": ai_result
        }