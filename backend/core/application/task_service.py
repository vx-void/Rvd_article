import uuid
from typing import Dict, Optional

from .dto import ResultDTO, ResultItemDTO


class TaskService:
    """
    Сервис управления состоянием задач.
    В рамках проектной реализации используется
    временное in-memory хранилище.
    """

    def __init__(self, repository) -> None:
        self._repository = repository
        self._tasks: Dict[str, ResultDTO] = {}

    def create_task(self) -> str:
        """
        Создание новой задачи.
        """
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = ResultDTO(
            task_id=task_id,
            status="PENDING",
            items=[]
        )
        return task_id

    def update_status(self, task_id: str, status: str) -> None:
        """
        Обновление статуса задачи.
        """
        if task_id in self._tasks:
            self._tasks[task_id].status = status

    def save_result(
        self,
        task_id: str,
        items: Optional[list[ResultItemDTO]]
    ) -> None:
        """
        Сохранение результата обработки.
        """
        if task_id in self._tasks:
            self._tasks[task_id].items = items or []
            self._tasks[task_id].status = "COMPLETED"

    def get_result(self, task_id: str) -> Optional[ResultDTO]:
        """
        Получение результата по идентификатору задачи.
        """
        return self._tasks.get(task_id)
