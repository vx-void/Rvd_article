from dataclasses import dataclass
from typing import Type, Dict, Any

from database.models.base_component import HydraulicComponent


@dataclass
class ComponentFilter:
    component_type: Type[HydraulicComponent]
    params: Dict[str, Any]
