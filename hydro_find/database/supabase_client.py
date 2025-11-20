# supabase_client.py
from typing import Any, Dict, List, Union
from config import Config
from supabase import create_client, Client
import os

class SupabaseClientModule:
    def __init__(self, supabase_url: str, supabase_key: str):
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL и SUPABASE_KEY должны быть заданы.")
        try:
            self.supabase: Client = create_client(supabase_url, supabase_key)
        except Exception as e:
            raise

    def _verify_connection(self):
        pass

    def get_client(self) -> Client:
        return self.supabase

    def select_records(self, table_name: str, filters: dict = None, columns: str = "*") -> dict[str, str] | list[Any]:
        try:
            query = self.supabase.table(table_name).select(columns)
            if filters:
                for key, value in filters.items():
                    # Простой парсер фильтров. Более сложные случаи могут потребовать
                    # более мощной логики или библиотеки для построения запросов.
                    if isinstance(value, str):
                        # Предполагаем формат "оператор.значение", например "eq.1", "gte.10", "in.(1,2,3)"
                        op_parts = value.split('.', 1)
                        if len(op_parts) == 2:
                            op, val = op_parts[0], op_parts[1]
                            # Преобразуем строковый оператор в метод запроса
                            if op == "eq":
                                query = query.eq(key, val)
                            elif op == "neq":
                                query = query.neq(key, val)
                            elif op == "gt":
                                query = query.gt(key, val)
                            elif op == "gte":
                                query = query.gte(key, val)
                            elif op == "lt":
                                query = query.lt(key, val)
                            elif op == "lte":
                                query = query.lte(key, val)
                            elif op == "like":
                                query = query.like(key, val)
                            # elif op == "in": # Пример для in, val должно быть в формате "(1,2,3)"
                            #     # Нужно аккуратно обработать строку val
                            #     pass
                            else:
                                query = query.eq(key, val)
                        else:
                            query = query.eq(key, value) # Если формат не "op.val", используем eq
                    else:
                        query = query.eq(key, value) # Для не-строковых значений используем eq

            response = query.execute()
            return response.data
        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    try:
        sb_module = SupabaseClientModule(Config.SUPABASE_URL, Config.SUPABASE_KEY)

        bsp = '06 BSP 1/2" (0)(Г)'.replace(' ', '\u00A0')
        result = sb_module.select_records("fittings", {"name": bsp}, columns='article')
        print(result)
    except ValueError as ve:
        print(f"Ошибка конфигурации: {ve}")
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
