import os
from dotenv import load_dotenv
from typing import Any, Dict, List
from supabase import create_client, Client

load_dotenv()

from backend.config import Config

from backend.data.repositories.entity import Entity
from backend.data.repositories.fitting import Fitting


class SupabaseClientModule:
    def __init__(self, supabase_url=None, supabase_key=None):

        self.supabase_url = supabase_url or Config.SUPABASE_URL
        self.supabase_key = supabase_key or Config.SUPABASE_KEY

        # DEBUG
        print(f"URL: {self.supabase_url}")
        print(f"Key present: {bool(self.supabase_key)}")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL и SUPABASE_KEY должны быть заданы.")

        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        except Exception as e:
            raise RuntimeError(f"Ошибка подключения к Supabase: {e}")

    def get_client(self) -> Client:
        return self.supabase

    def execute_query(self, entity: Entity) -> List[Dict[str, Any]]:
        try:
            table_name = entity.table_name
            filters = entity.to_dict()

            query = self.supabase.table(table_name).select('*')

            for key, value in filters.items():
                if value is not None:
                    if isinstance(value, bool):
                        query = query.eq(key, value)
                    elif isinstance(value, str) and key == 's_key':
                        query = query.ilike(key, f'%{value}%')
                    else:
                        query = query.eq(key, value)

            response = query.execute()
            return response.data

        except Exception as e:
            raise RuntimeError(f"Ошибка выполнения запроса: {e}")

    def get_fittings(self, **filters) -> List[Dict[str, Any]]:
        fitting = Fitting.from_filters(**filters)
        return self.execute_query(fitting)


if __name__ == "__main__":
    try:

        print("Проверка переменных окружения:")
        print("SUPABASE_URL из os.environ:", os.environ.get('SUPABASE_URL'))
        print("SUPABASE_KEY из os.environ:", bool(os.environ.get('SUPABASE_KEY')))

        sb_module = SupabaseClientModule()

        fittings = sb_module.get_fittings(
            standard='BSP',
            thread='3/4',
            Dy=20
        )
        print(f"Найдено фитингов: {len(fittings)}")


        bsp_name = '06 BSP 1/2" (0)(Г)'.replace(' ', '\u00A0')
        result = sb_module.supabase.table("fittings") \
            .select('article') \
            .eq('name', bsp_name) \
            .execute()
        print(result.data)

    except Exception as e:
        print(f"Ошибка: {e}")