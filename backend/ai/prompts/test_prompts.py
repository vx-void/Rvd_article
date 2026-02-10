# test_prompt_files.py
#!/usr/bin/env python3
"""
Тестирование загрузки промптов из файлов
"""

import sys
from pathlib import Path

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent))

from ai.prompts.repository import PromptRepository
from ai.prompts.types import ComponentType, PreprocessingTask


def test_prompt_loading():
    """Тест загрузки промптов из файлов"""
    print("🧪 Тестирование загрузки промптов из файлов")
    print("=" * 50)
    
    try:
        # Создаем репозиторий
        repo = PromptRepository()
        
        print(f"Директория промптов: {repo.prompts_dir}")
        print()
        
        # Тестируем загрузку промптов предобработки
        print("Промпты предобработки:")
        for task in PreprocessingTask:
            try:
                prompt = repo.get_preprocessing_prompt(task)
                print(f"  {task.value}: {prompt[:80]}...")
            except Exception as e:
                print(f"  {task.value}: ОШИБКА - {e}")
        
        print()
        
        # Тестируем загрузку промптов компонентов
        print("🔧 Промпты компонентов:")
        for component in ComponentType:
            try:
                prompt = repo.get_component_prompt(component)
                print(f"  {component.value}: {prompt[:80]}...")
            except Exception as e:
                print(f"  {component.value}: ОШИБКА - {e}")
        
        print()
        print("Тест загрузки промптов завершен успешно!")
        
        # Показываем содержимое директории
        print("\nФайлы в директории промптов:")
        for file_path in repo.prompts_dir.glob("*"):
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"  - {file_path.name} ({size} байт)")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


def test_fittings_prompt():
    """Тест загрузки промпта для фитингов"""
    print("\nТестирование промпта для фитингов")
    print("=" * 50)
    
    try:
        repo = PromptRepository()
        
        # Загружаем промпт для фитингов
        prompt = repo.get_component_prompt(ComponentType.FITTINGS)
        
        print(f"Промпт для фитингов (первые 200 символов):")
        print("-" * 50)
        print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
        print("-" * 50)
        
        # Проверяем содержимое промпта
        required_keywords = ["фитинг", "JSON", "standard", "Dy"]
        missing_keywords = []
        
        for keyword in required_keywords:
            if keyword.lower() not in prompt.lower():
                missing_keywords.append(keyword)
        
        if missing_keywords:
            print(f"В промпте отсутствуют ключевые слова: {missing_keywords}")
        else:
            print("Промпт содержит все необходимые ключевые слова")
        
        print(f"Длина промпта: {len(prompt)} символов")
        
    except Exception as e:
        print(f"Ошибка: {e}")


def save_test_prompts():
    """Сохранение тестовых промптов"""
    print("\Сохранение тестовых промптов")
    print("=" * 50)
    
    try:
        repo = PromptRepository()
        
        # Сохраняем расширенный промпт для фитингов
        detailed_fittings_prompt = """Ты - специалист по фитингам

Проанализируй запрос и извлеки параметры фитинга в виде одного JSON-объекта, соответствующего стандарту.

Общие правила:
- Включай только те поля, которые явно упомянуты в тексте
- Поле "standard" определяется по ключевым словам в тексте
- Значение "Dy" — внутренний диаметр шланга

Поля:
- standard: строка (обязательное)
- Dy: целое число
- thread: строка
- armature: строка
- angle: целое число
- removable_nut: boolean
- o_ring: boolean

Верни результат строго в формате JSON.
Не добавляй пояснений, комментариев или дополнительного текста."""

        repo.save_component_prompt(ComponentType.FITTINGS, detailed_fittings_prompt)
        print("Тестовый промпт для фитингов сохранен")
        
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    print("Запуск тестов загрузки промптов из файлов")
    print()
    
    # Создаем директорию для промптов, если её нет
    prompts_dir = Path("ai/prompts/files")
    prompts_dir.mkdir(parents=True, exist_ok=True)
    
    # Запускаем тесты
    test_prompt_loading()
    test_fittings_prompt()
    
    # Опционально: сохраняем тестовые промпты
    save_option = input("\nСохранить тестовые промпты? (да/нет): ").strip().lower()
    if save_option in ['да', 'yes', 'y', 'д']:
        save_test_prompts()
    
    print("\nТестирование завершено!")