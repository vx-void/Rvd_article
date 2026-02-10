from typing import List

from backend.core.messaging.consumer import RabbitMQConsumer
from backend.core.messaging.message import Message

from backend.core.application.task_service import TaskService
from backend.core.application.dto import ResultItemDTO

from backend.ai.service import AIService
from backend.database.repository import ComponentRepository
from backend.database.component_filter import ComponentFilter


class SearchWorker:
    """
    Асинхронный обработчик задач поиска.
    """

    def __init__(
        self,
        task_service: TaskService,
        ai_service: AIService,
        repository: ComponentRepository
    ) -> None:
        self._task_service = task_service
        self._ai_service = ai_service
        self._repository = repository

    def handle_message(self, message: Message) -> None:
        """
        Основной сценарий обработки сообщения.
        """

        task_id = message.task_id
        query = message.payload.get("query", "")

        try:
            # 1. Обновление статуса
            self._task_service.update_status(task_id, "IN_PROGRESS")

            # 2. Извлечение параметров через AI
            extraction_result = self._ai_service.process(query)

            # 3. Формирование фильтра
            component_filter = ComponentFilter(
                component_type=extraction_result.component_type,
                parameters=extraction_result.parameters
            )

            # 4. Поиск в базе данных
            components = self._repository.find(component_filter)

            # 5. Преобразование в DTO
            result_items: List[ResultItemDTO] = [
                ResultItemDTO(
                    article=component.article,
                    name=component.name,
                    quantity=extraction_result.quantity
                )
                for component in components
            ]

            # 6. Сохранение результата
            self._task_service.save_result(task_id, result_items)

        except Exception:
            self._task_service.update_status(task_id, "FAILED")
            raise


def start_worker(
    host: str,
    queue_name: str,
    task_service: TaskService,
    ai_service: AIService,
    repository: ComponentRepository
) -> None:
    """
    Инициализация и запуск worker-процесса.
    """

    worker = SearchWorker(
        task_service=task_service,
        ai_service=ai_service,
        repository=repository
    )

    consumer = RabbitMQConsumer(
        host=host,
        queue_name=queue_name,
        callback=worker.handle_message
    )

    consumer.start()
