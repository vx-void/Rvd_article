from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class TaskDTO:
    """
    Объект передачи данных, описывающий задачу обработки запроса.
    """
    task_id: str
    status: str


@dataclass
class ResultItemDTO:
    """
    Представление одного найденного компонента.
    """
    article: str
    name: str
    quantity: Optional[int] = None


@dataclass
class ResultDTO:
    """
    Результат выполнения задачи.
    """
    task_id: str
    status: str
    items: List[ResultItemDTO]


@dataclass
class SearchCommand:
    """
    Команда на выполнение поиска.
    """
    query: str
