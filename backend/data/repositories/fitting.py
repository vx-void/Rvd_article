from backend.data.models.components import FittingDTO, ArmatureType
from backend.data.repositories.base import BaseRepository
from typing import Dict, Any

class FittingRepository(BaseRepository):
    table_name = "fittings"

    def __init__(self, dto: FittingDTO):
        self.dto = dto

    def get_filters(self) -> Dict[str, Any]:
        # Преобразуем Enum → str для Supabase
        filters = {}
        for field, value in self.dto.__dict__.items():
            if value is not None:
                if isinstance(value, ArmatureType):
                    filters[field] = value.value
                else:
                    filters[field] = value
        return filters