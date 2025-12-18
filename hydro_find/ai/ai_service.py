# hydro_find/ai/ai_service.py

from typing import Optional, Dict, Any, List
from datetime import datetime
from hydro_find.ai.openrouter_client import ComponentClassifier, ComponentModel
from hydro_find.ai.prompts import get_component_prompt, get_preprocessing_prompt


class AIProcessingService:
    """
    Сервис для полной обработки запроса с использованием ИИ.
    Поддерживает многоступенчатую обработку:
    1. Разбиение списка (если нужно)
    2. Классификация типа компонента
    3. Извлечение параметров
    4. Извлечение количества
    """

    def __init__(self):
        self.classifier = ComponentClassifier()

    # === Этап 1: Предобработка ===

    def split_input_lines(self, text: str) -> List[str]:
        """Разбивает входной текст на отдельные строки компонентов."""
        model = ComponentModel(get_preprocessing_prompt("split"))
        result = model.client.generate_response(
            system_prompt=get_preprocessing_prompt("split"),
            user_query=text
        )
        if not result:
            return [text]  # fallback: treat as single line

        # Разделяем по символу новой строки
        return [line.strip() for line in result.strip().split('\n') if line.strip()]

    def extract_quantity(self, line: str) -> Optional[int]:
        """Извлекает количество из строки компонента."""
        model = ComponentModel(get_preprocessing_prompt("quantity"))
        result = model.client.generate_response(
            system_prompt=get_preprocessing_prompt("quantity"),
            user_query=line
        )
        if not result:
            return None

        result = result.strip()
        if result == "Не указано":
            return None

        # Извлекаем первое число
        digits = ''.join(filter(str.isdigit, result))
        return int(digits) if digits else None

    # === Этап 2: Классификация ===

    def classify_component(self, query: str) -> Optional[str]:
        """Классифицирует компонент: возвращает строку вида 'fittings'."""
        return self.classifier.classify(query)

    # === Этап 3: Извлечение параметров ===

    def extract_parameters(self, query: str, component_type: str) -> Optional[Dict[str, Any]]:
        """Извлекает параметры по типу компонента."""
        try:
            prompt = get_component_prompt(component_type)
        except ValueError as e:
            raise ValueError(f"Нет промпта для типа '{component_type}': {e}")

        model = ComponentModel(prompt)
        return model.extract_json(query)

    # === Основной метод обработки ===

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Обрабатывает одиночный запрос (один компонент).
        Возвращает структурированный результат с параметрами и количеством.
        """
        timestamp = datetime.now().isoformat()

        try:
            # Шаг 1: Классификация
            component_type = self.classify_component(query)
            if not component_type:
                return self._error_result("Не удалось определить тип компонента", timestamp)

            # Шаг 2: Извлечение параметров
            extracted = self.extract_parameters(query, component_type)
            if not extracted:
                return self._error_result("Не удалось извлечь параметры", timestamp)

            # Шаг 3: Извлечение количества
            quantity = self.extract_quantity(query)

            return {
                "success": True,
                "component_type": component_type,
                "original_query": query,
                "extracted_data": extracted,
                "quantity": quantity,
                "timestamp": timestamp
            }

        except Exception as e:
            return self._error_result(f"Ошибка ИИ-обработки: {e}", timestamp)

    def process_batch_query(self, text: str) -> Dict[str, Any]:
        """
        Обрабатывает пакетный запрос (список компонентов).
        Сначала разбивает на строки, затем обрабатывает каждую.
        """
        timestamp = datetime.now().isoformat()

        try:
            # Шаг 0: Разбиение на строки
            lines = self.split_input_lines(text)

            results = []
            for line in lines:
                result = self.process_query(line)
                results.append(result)

            return {
                "success": True,
                "batch": True,
                "results": results,
                "total_items": len(lines),
                "timestamp": timestamp
            }

        except Exception as e:
            return self._error_result(f"Ошибка пакетной обработки: {e}", timestamp)

    # === Вспомогательные методы ===

    def _error_result(self, message: str, timestamp: str) -> Dict[str, Any]:
        return {
            "success": False,
            "error": message,
            "timestamp": timestamp
        }