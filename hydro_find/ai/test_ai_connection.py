# test_ai_connection.py
import logging
import sys

logging.basicConfig(level=logging.DEBUG)

from hydro_find.ai.service import AIProcessingService

def test_ai():
    try:
        print("Тестирование подключения к OpenRouter...")
        service = AIProcessingService()

        # Тестовый запрос
        test_query = "фитинг гидравлический 1/2 BSP 90 градусов"
        print(f"\nОтправка запроса: {test_query}")

        result = service.process_single(test_query)

        print(f"\nРезультат:")
        print(f"Успех: {result.get('success')}")
        print(f"Тип компонента: {result.get('component_type')}")
        print(f"Параметры: {result.get('extracted_data')}")

        # Проверка здоровья
        health = service.health_check()
        print(f"\nHealth Check: {health.get('status')}")

    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_ai()