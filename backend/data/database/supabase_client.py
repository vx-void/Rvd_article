import os
from supabase import create_client, Client
from backend.config import Config
from backend.data.repositories.base import BaseRepository
from typing import Any, Dict, List

class SupabaseClientModule:
    def __init__(self):
        supabase_url = Config.SUPABASE_URL
        supabase_key = Config.SUPABASE_KEY
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL и SUPABASE_KEY должны быть заданы.")
        self.client: Client = create_client(supabase_url, supabase_key)

    def execute_query(self, repo: BaseRepository) -> List[Dict[str, Any]]:
        table = self.client.table(repo.table_name)
        filters = repo.get_filters()
        query = table.select("name,article")
        for key, value in filters.items():
            if isinstance(value, bool):
                query = query.eq(key, value)
            elif isinstance(value, str) and key == "s_key":
                query = query.ilike(key, f"%{value}%")
            else:
                query = query.eq(key, value)
        return query.execute().data

    def get_fittings(self, **filters) -> List[Dict[str, Any]]:
        from backend.data.models.components import FittingDTO
        from backend.data.repositories.fitting import FittingRepository
        dto = FittingDTO(**filters)
        repo = FittingRepository(dto)
        return self.execute_query(repo)