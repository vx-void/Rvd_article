# database/repository/supabase_repository.py
from typing import Type, List
from supabase import Client

from backend.database.interfaces.repository import ComponentRepositoryInterface
from backend.database.filters.component_filter import ComponentFilter


class SupabaseComponentRepository(ComponentRepositoryInterface):

    def __init__(self, client: Client):
        self.client = client

    def find(self, filters: ComponentFilter) -> List[dict]:
        table = self._resolve_table(filters.component_type)

        query = (
            self.client
            .schema("public")
            .table(table)
            .select("*")
        )

        for field, value in filters.params.items():
            if value is not None:
                query = query.eq(field, value)

        response = query.execute()

        return response.data

    @staticmethod
    def _resolve_table(component_type: Type) -> str:
        return component_type.__tablename__
