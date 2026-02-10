from abc import ABC, abstractmethod
from typing import List

from database.models.base_component import HydraulicComponent
from database.filters.component_filter import ComponentFilter


class IComponentRepository(ABC):

    @abstractmethod
    def find(self, filters: ComponentFilter) -> List[HydraulicComponent]:
        pass
