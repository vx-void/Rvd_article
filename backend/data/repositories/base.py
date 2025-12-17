from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseRepository(ABC):
    table_name: str

    @abstractmethod
    def get_filters(self) -> Dict[str, Any]:
        pass