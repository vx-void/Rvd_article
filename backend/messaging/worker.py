# backend/messaging/worker.py

from ..services.ai_service import AIService
from ..services.db_service import DBService
from ..services.cache_service import CacheService
from ..reporting.excel_service import ExcelService
import hashlib

class RMQWorker:
    def __init__(self):
        self._ai = AIService()
        self._db = DBService()
        self._cache = CacheService()
        self._excel = ExcelService("results.xlsx")

    def process_message(self, message: dict) -> dict:
        user_query = message.get('query', '')
        task_id = message.get('task_id', '')

        # 1. Обработка ИИ
        ai_result = self._ai.process_single(user_query)

        if not ai_result["success"]:
            self._cache.set_task_status(task_id, "error", {"error": ai_result["error"]})
            return {
                "task_id": task_id,
                "error": ai_result["error"]
            }

        # 2. Поиск в БД
        matches = self._db.search_by_ai_params({
            "component_type": ai_result["component_type"],
            "original_query": user_query,
            **ai_result["extracted_data"]
        })

        # 3. Сохранить результат в кэш
        query_hash = hashlib.md5(user_query.encode()).hexdigest()
        self._cache.cache_search_result(query_hash, matches)

        # 4. Сохранить отчет в Excel
        if matches:
            for match in matches:
                self._excel.write(
                    query=user_query,
                    name=match.get("name", ""),
                    article=match.get("article", ""),
                    quantity=message.get("quantity", 1)
                )

        # 5. Сохранить путь к Excel в кэш
        excel_path = self._excel.filename
        self._cache.cache_excel_path(task_id, excel_path)

        # 6. Обновить статус задачи
        result = {
            "source": "database" if matches else "ai_only",
            "matches": matches,
            "ai_result": ai_result
        }
        self._cache.set_task_status(task_id, "completed", result)

        return {
            "task_id": task_id,
            "result": result
        }