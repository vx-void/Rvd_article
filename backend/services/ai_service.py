
import json
from datetime import datetime
from typing import Dict, Any, List
from ai.processing.extractors import extract_component_info


class ComponentProcessingService:
    def __init__(self):
        pass

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Args:
            query: Запрос пользователя

        Returns:
            Результат обработки
        """
        try:
            print(f"[{datetime.now()}] Обработка запроса: {query}")

            # Извлечение информации о компоненте
            result = extract_component_info(query)

            # Логирование результата
            self._log_result(result)

            return result

        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Ошибка обработки запроса: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            print(f"[{datetime.now()}] {error_result['error']}")
            return error_result

    def process_batch(self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Args:
            queries: Список запросов

        Returns:
            Список результатов
        """
        results = []
        for query in queries:
            result = self.process_query(query)
            results.append(result)

        return results

    def _log_result(self, result: Dict[str, Any]) -> None:
        if result.get("success"):
            component_type = result.get("component_type", "unknown")
            print(f"[{datetime.now()}] Успешно обработан тип: {component_type}")
        else:
            print(f"[{datetime.now()}] Ошибка: {result.get('error', 'Неизвестная ошибка')}")


def process_component_query(query: str) -> Dict[str, Any]:
    """
    Args:
        query: Запрос пользователя

    Returns:
        Результат обработки
    """
    service = ComponentProcessingService()
    return service.process_query(query)


if __name__ == '__main__':
    # Тестовые запросы
    test_queries = [
        'ФИТИНГ DK(Г) 0° 20*1,5 DN10 20111-20-06 — 150 шт.',
        'Адаптер BSP штуцер 3/4 на гайку 1/2',
        'Заглушка JIC 3/4',
        'Тройник DKOL Ш-к 10х1.5, Г 3/4, Ш 1/2'
    ]

    service = ComponentProcessingService()

    print("=" * 60)
    print("ТЕСТИРОВАНИЕ СЕРВИСА ОБРАБОТКИ КОМПОНЕНТОВ")
    print("=" * 60)

    for i, query in enumerate(test_queries, 1):
        print(f"\nТест {i}: {query}")
        print("-" * 40)

        result = service.process_query(query)

        if result.get("success"):
            print(f"Тип компонента: {result.get('component_type')}")
            print("Извлеченные данные:")
            print(json.dumps(result.get('extracted_data', {}),
                             ensure_ascii=False, indent=2))
        else:
            print(f"Ошибка: {result.get('error')}")