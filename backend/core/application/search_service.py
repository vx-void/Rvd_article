from typing import Protocol

from .dto import TaskDTO, SearchCommand
from .task_service import TaskService


class MessageBroker(Protocol):
    """
    Абстракция брокера сообщений.
    """

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
        self._task_service = task_service
        self._message_broker = message_broker

    def execute(self, command: SearchCommand) -> TaskDTO:
        """
        Инициация обработки поискового запроса.
        """

        self._validate(command)

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

    def _validate(self, command: SearchCommand) -> None:
        """
        Валидация входного запроса.
        """
        if not command.query:
            raise ValueError("Search query must not be empty")

        if len(command.query) > 1024:
            raise ValueError("Search query exceeds maximum length")
