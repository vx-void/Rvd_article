from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Entity(ABC):
    def __init__(self):
        self.base_query = 'SELECT name, article FROM public.'
        self.table_name = None

    @abstractmethod
    def get_query(self) -> str:
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {key: value for key, value in self.__dict__.items()
                if not key.startswith('_') and value is not None and key not in ['base_query', 'query', 'component']}