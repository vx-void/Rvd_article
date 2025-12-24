import hashlib
import logging
from ..services.ai_service import AIService
from ..services.db_service import DBService
from ..services.cache_service import CacheService
from ..services.excel_service import ExcelService

logger = logging.getLogger(__name__)


class RMQWorker:
    def __init__(self):
        self._ai = AIService()
        self._db = DBService()
        self._cache = CacheService()
        self._excel = ExcelService()

    @property
    def excel(self):
        """Геттер для ExcelService"""
        return self._excel

    def process_message(self, message: dict) -> dict:
        user_query = message.get('query', '')
        task_id = message.get('task_id', '')

        logger.info(f"Starting processing for task {task_id}")

        # 1. Обработка ИИ
        try:
            ai_result = self._ai.process_single(user_query)

            if not ai_result.get("success"):
                error_msg = ai_result.get("error", "Unknown AI error")
                self._cache.set_task_status(task_id, "error", {"error": error_msg})
                logger.error(f"AI processing failed for task {task_id}: {error_msg}")
                return {
                    "task_id": task_id,
                    "error": error_msg,
                    "status": "error"
                }
        except Exception as e:
            error_msg = f"AI service error: {str(e)}"
            self._cache.set_task_status(task_id, "error", {"error": error_msg})
            logger.error(f"AI service exception for task {task_id}: {e}")
            return {
                "task_id": task_id,
                "error": error_msg,
                "status": "error"
            }

        # 2. Поиск в БД
        try:
            search_params = {
                "component_type": ai_result["component_type"],
                "original_query": user_query,
                **ai_result["extracted_data"]
            }
            matches = self._db.search_by_ai_params(search_params)
            logger.info(f"Found {len(matches)} matches for task {task_id}")
        except Exception as e:
            error_msg = f"Database search error: {str(e)}"
            self._cache.set_task_status(task_id, "error", {"error": error_msg})
            logger.error(f"Database error for task {task_id}: {e}")
            return {
                "task_id": task_id,
                "error": error_msg,
                "status": "error"
            }

        # 3. Сохранить результат в кэш
        try:
            query_hash = hashlib.md5(user_query.encode()).hexdigest()
            self._cache.cache_search_result(query_hash, matches)

            # 4. Сохранить отчет в Excel (если есть результаты)
            excel_path = None
            if matches:
                for match in matches:
                    self._excel.write(
                        query=user_query,
                        name=match.get("name", ""),
                        article=match.get("article", ""),
                        quantity=message.get("quantity", 1)
                    )
                excel_path = self._excel._filename
                self._cache.cache_excel_path(task_id, excel_path)

            # 5. Обновить статус задачи
            result = {
                "source": "database" if matches else "ai_only",
                "matches": matches,
                "ai_result": ai_result,
                "excel_path": excel_path
            }
            self._cache.set_task_status(task_id, "completed", result)

            logger.info(f"Task {task_id} completed successfully")
            return {
                "task_id": task_id,
                "result": result,
                "status": "completed"
            }

        except Exception as e:
            error_msg = f"Cache/Excel error: {str(e)}"
            self._cache.set_task_status(task_id, "error", {"error": error_msg})
            logger.error(f"Cache/Excel error for task {task_id}: {e}")
            return {
                "task_id": task_id,
                "error": error_msg,
                "status": "error"
            }