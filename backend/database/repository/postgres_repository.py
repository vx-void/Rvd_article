# database/repository/postgres_repository.py
from typing import Type, List
from psycopg import Connection
from psycopg.rows import dict_row

from backend.database.interfaces.repository import ComponentRepositoryInterface
from backend.database.filters.component_filter import ComponentFilter


class PostgresComponentRepository(ComponentRepositoryInterface):

    def __init__(self, connection: Connection):
        self.connection = connection

    def find(self, filters: ComponentFilter) -> List[dict]:
        table = self._resolve_table(filters.component_type)
        where_clause, values = self._build_where(filters.params)

        sql = f"""
            SELECT *
            FROM public.{table}
            {where_clause}
        """

        with self.connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(sql, values)
            return cursor.fetchall()

    @staticmethod
    def _resolve_table(component_type: Type) -> str:
        return component_type.__tablename__

    @staticmethod
    def _build_where(params: dict):
        conditions = []
        values = []

        for field, value in params.items():
            if value is not None:
                conditions.append(f"{field} = %s")
                values.append(value)

        if not conditions:
            return "", []

        return "WHERE " + " AND ".join(conditions), values
