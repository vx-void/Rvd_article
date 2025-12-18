# hydro_find/ai/classifiers.py

from typing import Optional
from hydro_find.ai.openrouter_client import ComponentClassifier
from backend.data.types.types import ComponentType  # или from hydro_find.models.types import ComponentType


def hydrofind(user_query: str) -> Optional[ComponentType]:
    """
    Классифицирует тип гидравлического компонента в запросе пользователя.

    Args:
        user_query (str): Текстовый запрос, например: "Фитинг DKOL 12x1.5"

    Returns:
        ComponentType | None: Тип компонента из перечисления или None при ошибке.
    """
    try:
        classifier = ComponentClassifier()
        component_type = classifier.classify(user_query)
        return component_type
    except Exception as e:
        print(f"❌ Ошибка в hydrofind: {e}")
        return None


if __name__ == '__main__':
    test_query = "Фитинг DKI 27x1,5 90 Dy12, RVD-Group"
    result = hydrofind(test_query)
    print(f"Результат: {result} (тип: {type(result)})")