from typing import Optional, Protocol, List
from .dto import TaskDTO, SearchCommand, ResultDTO, QueryResultDTO, MatchDTO
from .task_service import TaskService
import logging

logger = logging.getLogger(__name__)


class MessageBroker(Protocol):
    def publish(self, message: dict) -> None:
        ...


class ComponentRepository(Protocol):
    """
    Репозиторий для работы с компонентами в БД.
    """
    def find_by_query(self, query: str) -> List[MatchDTO]:
        ...

    def find_by_parameters(self, component_type: str, params: dict) -> List[MatchDTO]:
        ...


class QueryParser(Protocol):
    """
    Парсер текстового запроса.
    """
    def parse(self, text: str) -> List[QueryResultDTO]:
        ...


class SearchService:
    """
    Прикладной сервис обработки поискового запроса.
    Отвечает за оркестрацию сценария выполнения.
    """

    def __init__(
            self,
            task_service: TaskService,
            message_broker: MessageBroker,
            component_repository: Optional[ComponentRepository] = None,
            query_parser: Optional[QueryParser] = None
    ) -> None:
        if task_service is None:
            raise ValueError("task_service cannot be None")
        if message_broker is None:
            raise ValueError("message_broker cannot be None")

        self._task_service = task_service
        self._message_broker = message_broker
        self._component_repository = component_repository
        self._query_parser = query_parser

    def execute(self, command: SearchCommand) -> TaskDTO:
        """
        Инициация обработки поискового запроса.
        """
        self._validate(command)

        task_id = None
        try:
            # 1. Создание задачи
            task_id = self._task_service.create_task(command.query)
            
            # Если есть репозиторий и парсер, можно сразу выполнить поиск
            if self._component_repository and self._query_parser:
                # Парсим запрос
                parsed_queries = self._query_parser.parse(command.query)
                
                # Для каждого запроса ищем компоненты
                all_results = []
                for parsed_query in parsed_queries:
                    matches = self._component_repository.find_by_parameters(
                        parsed_query.component_type or "",
                        parsed_query.parameters
                    )
                    
                    result = QueryResultDTO(
                        original_query=parsed_query.original_query,
                        component_type=parsed_query.component_type,
                        parameters=parsed_query.parameters,
                        quantity=parsed_query.quantity,
                        matches=matches
                    )
                    all_results.append(result)
                
                # Сохраняем результат
                self._task_service.save_result(task_id, all_results)
                
                return TaskDTO(
                    task_id=task_id,
                    status="COMPLETED",
                    query=command.query
                )
            else:
                # 2. Формирование сообщения для асинхронной обработки
                message = {
                    "task_id": task_id,
                    "query": command.query,
                    "priority": command.priority
                }

                # 3. Публикация в очередь
                self._message_broker.publish(message)

                # 4. Возврат клиенту идентификатора задачи
                return TaskDTO(
                    task_id=task_id,
                    status="PENDING",
                    query=command.query
                )

        except Exception as e:
            # Если ошибка, обновляем статус задачи
            if task_id:
                self._task_service.update_status(task_id, "FAILED", str(e))
            
            logger.error(f"Failed to execute search: {e}")
            raise

    def get_status(self, task_id: str) -> Optional[ResultDTO]:
        """
        Получение статуса задачи по ID.
        """
        if not task_id:
            raise ValueError("task_id cannot be empty")

        return self._task_service.get_result(task_id)

    def search_sync(self, query: str) -> List[QueryResultDTO]:
        """
        Синхронный поиск (для простых запросов).
        """
        if not self._component_repository or not self._query_parser:
            raise RuntimeError("Component repository or query parser not configured")
        
        parsed_queries = self._query_parser.parse(query)
        results = []
        
        for parsed_query in parsed_queries:
            matches = self._component_repository.find_by_parameters(
                parsed_query.component_type or "",
                parsed_query.parameters
            )
            
            result = QueryResultDTO(
                original_query=parsed_query.original_query,
                component_type=parsed_query.component_type,
                parameters=parsed_query.parameters,
                quantity=parsed_query.quantity,
                matches=matches
            )
            results.append(result)
        
        return results

    def _validate(self, command: SearchCommand) -> None:
        """
        Валидация входного запроса.
        """
        if not command.query or not command.query.strip():
            raise ValueError("Search query must not be empty")

        if len(command.query) > 10000:  # Увеличим лимит
            raise ValueError("Search query exceeds maximum length (10000 chars)")

        # Дополнительная валидация
        if not isinstance(command.query, str):
            raise ValueError("Search query must be a string")
        
        if command.priority not in [1, 2, 3]:
            raise ValueError("Priority must be 1, 2 or 3")