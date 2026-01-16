# backend/services/db_service.py

from backend.app.database.connection import DatabaseConnection
from backend.app.database.repository import ComponentRepository

class DBService:
    def __init__(self):
        self._db = DatabaseConnection()
        self._repo = ComponentRepository(self._db)

    def search_by_ai_params(self, params: dict) -> list:
        return self._repo.search(params)