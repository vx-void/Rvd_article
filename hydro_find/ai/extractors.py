from typing import Optional, Dict, Any
from hydro_find.ai.openrouter_client import ComponentModel, ComponentClassifier
from backend.data.types.types import ComponentType
from hydro_find.ai.promts.component_prompts import get_prompt_for_component


class ComponentExtractor:
    def __init__(self):
        self.classifier = ComponentClassifier()
        self.component_model = None

    def extract_component_data(
            self,
            query: str,
            component_type: Optional[ComponentType] = None
    ) -> Dict[str, Any]:
        """
        Args:
            query: Пользовательский запрос
            component_type: Тип компонента (если None - определяется автоматически)

        Returns:
            Словарь с извлеченными данными
        """
        try:
            # Классификация типа компонента
            if not component_type:
                component_type = self.classifier.classify(query)

            if not component_type:
                return self._create_error_result("Не удалось определить тип компонента")

            try:
                prompt = get_prompt_for_component(component_type)
            except ValueError as e:
                return self._create_error_result(str(e))

            # Извлечение данных
            self.component_model = ComponentModel(prompt)
            extracted_data = self.component_model.extract_json(query)

            if not extracted_data:
                return self._create_error_result("Не удалось извлечь данные")

            return self._format_result(
                component_type=component_type,
                extracted_data=extracted_data,
                original_query=query
            )

        except Exception as e:
            return self._create_error_result(f"Ошибка обработки: {str(e)}")

    def _format_result(
            self,
            component_type: ComponentType,
            extracted_data: Dict[str, Any],
            original_query: str
    ) -> Dict[str, Any]:
        """Форматирование результата"""
        from datetime import datetime

        result = {
            "component_type": component_type.value,
            "original_query": original_query,
            "extracted_data": extracted_data,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }

        return result

    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        from datetime import datetime

        return {
            "success": False,
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        }


def extract_component_info(query: str) -> Dict[str, Any]:
    """
    Args:
        query: Пользовательский запрос

    Returns:
        Результат извлечения
    """
    extractor = ComponentExtractor()
    return extractor.extract_component_data(query)