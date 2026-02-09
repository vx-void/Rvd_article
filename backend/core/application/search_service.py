from typing import Optional, Protocol
from .dto import TaskDTO, SearchCommand, ResultDTO
from .task_service import TaskService


class MessageBroker(Protocol):
    def publish(self, message: dict) -> None:
        ...


class SearchService:
    """
    Прикладной сервис обработки поискового запроса.
    Отвечает за оркестрацию сценария выполнения.
    """

    def __init__(
            self,
            task_service: TaskService,
            message_broker: MessageBroker
    ) -> None:
        if task_service is None:
            raise ValueError("task_service cannot be None")
        if message_broker is None:
            raise ValueError("message_broker cannot be None")

        self._task_service = task_service
        self._message_broker = message_broker

    def execute(self, command: SearchCommand) -> TaskDTO:
        """
        Инициация обработки поискового запроса.
        """
        self._validate(command)

        task_id = None
        try:
            # 1. Создание задачи
            task_id = self._task_service.create_task()

            # 2. Формирование сообщения
            message = {
                "task_id": task_id,
                "query": command.query,
            }

            # 3. Публикация в очередь
            self._message_broker.publish(message)

            # 4. Возврат клиенту идентификатора задачи
            return TaskDTO(
                task_id=task_id,
                status="PENDING"
            )

        except Exception as e:
            # Если ошибка, обновляем статус задачи
            if task_id:
                self._task_service.update_status(task_id, "FAILED")
            # Логируем ошибку
            # logger.error(f"Failed to execute search: {e}")
            raise

    def get_status(self, task_id: str) -> Optional[ResultDTO]:
        """
        Получение статуса задачи по ID.
        """
        if not task_id:
            raise ValueError("task_id cannot be empty")

        return self._task_service.get_result(task_id)

    def _validate(self, command: SearchCommand) -> None:
        """
        Валидация входного запроса.
        """
        if not command.query:
            raise ValueError("Search query must not be empty")

        if len(command.query) > 1024:
            raise ValueError("Search query exceeds maximum length")

        # Дополнительная валидация
        if not isinstance(command.query, str):
            raise ValueError("Search query must be a string")