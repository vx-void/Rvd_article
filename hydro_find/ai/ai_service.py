# hydro_find/ai/ai_service.py

from typing import Optional, Dict, Any
from datetime import datetime
from hydro_find.ai.openrouter_client import ComponentClassifier, ComponentModel
from hydro_find.ai.prompts.component_prompts import get_prompt_for_component


class AIProcessingService:
    """
    Единый сервис для обработки пользовательского запроса с использованием ИИ:
    1. Классификация типа компонента
    2. Извлечение параметров
    """

    def __init__(self):
        self.classifier = ComponentClassifier()

    def classify_component(self, query: str) -> Optional[str]:
        """Классифицирует компонент: возвращает строку вида 'fittings'."""
        return self.classifier.classify(query)

    def extract_parameters(self, query: str, component_type: str) -> Optional[Dict[str, Any]]:
        """Извлекает параметры по типу компонента."""
        try:
            prompt = get_prompt_for_component(component_type)
        except ValueError as e:
            raise ValueError(f"Нет промпта для типа '{component_type}': {e}")

        model = ComponentModel(prompt)
        return model.extract_json(query)

    def process_query(self, query: str) -> Dict[str, Any]:
        """Полная обработка запроса с форматированием результата."""
        timestamp = datetime.now().isoformat()

        try:
            component_type = self.classify_component(query)
            if not component_type:
                return self._error_result("Не удалось определить тип компонента", timestamp)

            extracted = self.extract_parameters(query, component_type)
            if not extracted:
                return self._error_result("Не удалось извлечь параметры", timestamp)

            return {
                "success": True,
                "component_type": component_type,
                "original_query": query,
                "extracted_data": extracted,
                "timestamp": timestamp
            }

        except Exception as e:
            return self._error_result(f"Ошибка ИИ-обработки: {e}", timestamp)

    def _error_result(self, message: str, timestamp: str) -> Dict[str, Any]:
        return {
            "success": False,
            "error": message,
            "timestamp": timestamp
        }