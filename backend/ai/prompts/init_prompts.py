
"""
Утилита для инициализации промптов из файла fittings.txt
"""

import sys
from pathlib import Path

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.prompts.repository import PromptRepository
from ai.prompts.types import ComponentType


def initialize_prompts_from_file(prompts_dir: str = None):
    """
    Инициализирует промпты из файла fittings.txt в текущей директории.
    
    Args:
        prompts_dir: Директория для сохранения промптов
    """
    # Создаем репозиторий
    repo = PromptRepository(prompts_dir)
    
    # Проверяем наличие файла fittings.txt в текущей директории
    current_dir = Path.cwd()
    fittings_file = current_dir / "fittings.txt"
    
    if fittings_file.exists():
        # Загружаем промпт из файла
        with open(fittings_file, 'r', encoding='utf-8') as f:
            fittings_prompt = f.read()
        
        # Сохраняем промпт для фитингов
        repo.save_component_prompt(ComponentType.FITTINGS, fittings_prompt)
        print(f"Промпт для фитингов успешно загружен из {fittings_file}")
    else:
        print(f"Файл fittings.txt не найден в {current_dir}")
        print("Создайте файл fittings.txt с промптом для фитингов и запустите эту утилиту снова.")
        
        # Создаем пример файла
        example_prompt = """Ты специалист по гидравлическим фитингам.
Проанализируй запрос и извлеки параметры фитинга.

Поля:
- standard: строка
- Dy: целое число
- thread: строка
- armature: строка
- angle: целое число
- removable_nut: boolean
- o_ring: boolean

Верни результат строго в формате JSON.
Не добавляй пояснений, комментариев или дополнительного текста."""


        
        with open(current_dir / "fittings.txt.example", 'w', encoding='utf-8') as f:
            f.write(example_prompt)
        print(f"Создан пример файла: {current_dir}/fittings.txt.example")
    
    # Проверяем созданные файлы
    print("\nСозданные файлы промптов:")
    for file_path in repo.prompts_dir.glob("*.txt"):
        print(f"  - {file_path.name}")


if __name__ == "__main__":
    prompts_dir = sys.argv[1] if len(sys.argv) > 1 else None
    initialize_prompts_from_file(prompts_dir)