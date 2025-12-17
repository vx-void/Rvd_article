import json
from datetime import datetime
from typing import Dict, Any, List
from ai.processing.extractors import extract_component_info
from backend.data.models.components import FittingDTO
from backend.data.repositories.fitting import FittingRepository
from backend.data.database.supabase_client import SupabaseClientModule

def _map_ai_to_dto(component_type: str, extracted_data: Dict) -> FittingDTO:
    """Преобразует словарь от AI в DTO (временно только для фитингов)"""
    if component_type != "fittings":
        raise NotImplementedError(f"Поддержка {component_type} не реализована")
    return FittingDTO(**extracted_data)

def process_component_query(query: str) -> Dict[str, Any]:
    try:
        # Шаг 1: Извлечение через AI
        ai_result = extract_component_info(query)
        if not ai_result.get("success"):
            return ai_result

        component_type = ai_result["component_type"]
        extracted_data = ai_result["extracted_data"]

        # Шаг 2: Валидация и маппинг в DTO
        dto = _map_ai_to_dto(component_type, extracted_data)

        # Шаг 3: Выполнение запроса к БД
        repo = FittingRepository(dto)
        db_client = SupabaseClientModule()
        db_results = db_client.execute_query(repo)

        # Шаг 4: Формирование финального ответа
        items = []
        for row in db_results:
            items.append({
                "original_subquery": ai_result["original_query"],
                "name": row["name"],
                "article": row["article"],
                "quantity": 1  # Пока без количества (реализуется отдельно)
            })

        return {
            "success": True,
            "items": items,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Ошибка обработки: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }