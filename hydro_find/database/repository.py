# hydro_find/database/repository.py

from typing import List, Dict, Any

from .connection import DatabaseConnection
from .models import CATEGORY_TO_MODEL
from .query_builder import ComponentQueryBuilder

class ComponentRepository:
    def __init__(self, db: DatabaseConnection):
        self._db = db

    def search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        category = params.get("component_type")
        model_class = CATEGORY_TO_MODEL.get(category)
        if not model_class:
            return []

        session = self._db.get_session()
        try:
            query = session.query(model_class)
            builder = ComponentQueryBuilder(query, params)
            results = builder.build().limit(10).all()
            return [item.to_dict() for item in results]
        finally:
            session.close()