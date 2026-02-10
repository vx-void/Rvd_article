from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict


@dataclass
class TaskDTO:
    """
    Объект передачи данных, описывающий задачу обработки запроса.
    """
    task_id: str
    status: str
    query: Optional[str] = None


@dataclass
class MatchDTO:
    """
    Представление одного найденного компонента.
    """
    article: str
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    manufacturer: Optional[str] = None


@dataclass
class QueryResultDTO:
    """
    Результат для одного запроса.
    """
    original_query: str
    component_type: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    quantity: int = 1
    matches: List[MatchDTO] = field(default_factory=list)


@dataclass
class ResultDTO:
    """
    Результат выполнения задачи.
    """
    task_id: str
    status: str
    results: List[QueryResultDTO] = field(default_factory=list)
    error: Optional[str] = None
    processed_at: Optional[str] = None


@dataclass
class SearchCommand:
    """
    Команда на выполнение поиска.
    """
    query: str
    priority: int = 1