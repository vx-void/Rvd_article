from abc import ABC, abstractmethod
from typing import List

from backend.database.models.base_component import HydraulicComponent
from backend.database.filters.component_filter import ComponentFilter


class IComponentRepository(ABC):

    @abstractmethod
    def find(self, filters: ComponentFilter) -> List[HydraulicComponent]:
        pass
