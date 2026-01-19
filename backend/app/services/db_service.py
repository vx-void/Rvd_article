# backend/services/db_service.py

from backend.app.database.connection import DatabaseConnection
from backend.app.database.repository import ComponentRepository

COMPONENT_TYPE_MAPPING ={
    'фитинг' : 'fittings',
    'адаптер' : 'adapters',
    'муфта' : 'couplings',
    'заглушка' : 'plugs',
    'адаптер-тройник':'adapter-tee',
    'banjo' : 'banjo'
}


class DBService:
    def __init__(self):
        self._db = DatabaseConnection()
        self._repo = ComponentRepository(self._db)

    def search_by_ai_params(self, params: dict) -> list:
        ru_type=params.get('component_type')
        en_type=COMPONENT_TYPE_MAPPING.get(ru_type.lower(), ru_type)
        params['component_type'] = en_type
        return self._repo.search(params)