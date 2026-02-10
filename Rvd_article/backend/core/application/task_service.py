import uuid
from typing import Dict, Optional, List
from datetime import datetime

from .dto import ResultDTO, QueryResultDTO


class TaskService:
    """
    Сервис управления состоянием задач.
    В рамках проектной реализации используется
    временное in-memory хранилище.
    """

    def __init__(self, repository=None) -> None:
        self._repository = repository
        self._tasks: Dict[str, ResultDTO] = {}
        self._task_queries: Dict[str, str] = {}  # task_id -> query

    def create_task(self, query: str = "") -> str:
        """
        Создание новой задачи.
        """
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = ResultDTO(
            task_id=task_id,
            status="PENDING",
            results=[]
        )
        self._task_queries[task_id] = query
        return task_id

    def update_status(self, task_id: str, status: str, error: Optional[str] = None) -> None:
        """
        Обновление статуса задачи.
        """
        if task_id in self._tasks:
            self._tasks[task_id].status = status
            if error:
                self._tasks[task_id].error = error
            if status in ["COMPLETED", "FAILED"]:
                self._tasks[task_id].processed_at = datetime.now().isoformat()

    def save_result(
        self,
        task_id: str,
        results: Optional[List[QueryResultDTO]] = None
    ) -> None:
        """
        Сохранение результата обработки.
        """
        if task_id in self._tasks:
            self._tasks[task_id].results = results or []
            self._tasks[task_id].status = "COMPLETED"
            self._tasks[task_id].processed_at = datetime.now().isoformat()

    def get_result(self, task_id: str) -> Optional[ResultDTO]:
        """
        Получение результата по идентификатору задачи.
        """
        return self._tasks.get(task_id)

    def get_task_query(self, task_id: str) -> Optional[str]:
        """
        Получение исходного запроса задачи.
        """
        return self._task_queries.get(task_id)

    def cleanup_old_tasks(self, hours: int = 24):
        """
        Очистка старых задач.
        """
        now = datetime.now()
        to_remove = []
        
        for task_id, task in self._tasks.items():
            if task.processed_at:
                processed = datetime.fromisoformat(task.processed_at)
                if (now - processed).total_seconds() > hours * 3600:
                    to_remove.append(task_id)
        
        for task_id in to_remove:
            self._tasks.pop(task_id, None)
            self._task_queries.pop(task_id, None)