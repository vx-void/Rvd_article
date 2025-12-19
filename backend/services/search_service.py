# backend/services/search_service.py

from hydro_find.ai.service import AIProcessingService
from hydro_find.database.connection import DatabaseConnection
from hydro_find.database.repository import ComponentRepository

class SearchService:
    def __init__(self):
        self._ai = AIProcessingService()
        self._db = DatabaseConnection()
        self._repo = ComponentRepository(self._db)

    def search(self, user_query: str) -> dict:
        # 1. Извлечение параметров ИИ
        ai_result = self._ai.process_single(user_query)
        if not ai_result["success"]:
            return ai_result

        # 2. Поиск в БД по извлечённым параметрам
        # ИИ возвращает, например: {"standard": "bsp", "armature": "гайка", "angle": 90}
        # QueryBuilder преобразует в: standard_id = Standard.BSP.value (1), armature_id = Armature.NUT.value (1) и т.д.
        db_params = {
            "component_type": ai_result["component_type"],
            "original_query": user_query,
            **ai_result["extracted_data"]
        }

        matches = self._repo.search(db_params)

        # 3. Формирование результата
        return {
            "success": True,
            "source": "database" if matches else "ai_only",
            "matches": matches,
            "ai_result": ai_result
        }