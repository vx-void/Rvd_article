# ai/prompts/repository.py
import os
from pathlib import Path
from typing import Dict

from ai.interfaces.prompt_repository import IPromptRepository
from ai.prompts.types import ComponentType, PreprocessingTask


class PromptRepository(IPromptRepository):
    """
    Репозиторий промптов, загружающий промпты из текстовых файлов.
    """
    
    def __init__(self, prompts_dir: str = None):
        """
        Инициализация репозитория промптов.
        
        Args:
            prompts_dir: Директория с промптами. Если не указана, используется
                        стандартная директория ai/prompts/files/
        """
        if prompts_dir is None:
            # Определяем базовую директорию относительно этого файла
            base_dir = Path(__file__).parent
            self.prompts_dir = base_dir / "files"
        else:
            self.prompts_dir = Path(prompts_dir)
        
        # Кэш для загруженных промптов
        self._component_prompts_cache: Dict[str, str] = {}
        self._preprocessing_prompts_cache: Dict[str, str] = {}
        
        # Проверяем существование директории
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Директория с промптами не найдена: {self.prompts_dir}")
        
        # Создаем директорию, если она не существует
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем стандартные файлы промптов
        self._initialize_prompt_files()
    
    def _initialize_prompt_files(self):
        """Инициализирует стандартные файлы промптов, если они отсутствуют."""
        # Файлы для предобработки
        preprocessing_files = {
            "classify.txt": """Определи тип гидравлического компонента.
Возможные значения:
fittings, adapters, plugs, adapter-tee, banjo, banjo-bolt, brs, coupling.

Ответь одним словом.

ПРАВИЛА:
1. Не добавляй комментариев
2. Сохраняй исходное написание
3. Следуй формату вывода""",
            
            "quantity.txt": """Извлеки количество компонентов из запроса.
Ответь числом или 'не указано'.

ПРАВИЛА:
1. Не добавляй комментариев
2. Сохраняй исходное написание
3. Следуй формату вывода""",
            
            "split.txt": """Раздели текст на отдельные позиции, по одной на строку.

ПРАВИЛА:
1. Не добавляй комментариев
2. Сохраняй исходное написание
3. Следуй формату вывода"""
        }
        
        # Создаем файлы предобработки
        for filename, content in preprocessing_files.items():
            file_path = self.prompts_dir / filename
            if not file_path.exists():
                file_path.write_text(content, encoding='utf-8')
                print(f"Создан файл промпта: {file_path}")
    
    def _load_prompt_from_file(self, filename: str) -> str:
        """
        Загружает промпт из файла.
        
        Args:
            filename: Имя файла с промптом
            
        Returns:
            Содержимое файла с промптом
            
        Raises:
            FileNotFoundError: Если файл не найден
        """
        file_path = self.prompts_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл промпта не найден: {file_path}")
        
        return file_path.read_text(encoding='utf-8').strip()
    
    def get_component_prompt(self, component: ComponentType) -> str:
        """
        Получает промпт для указанного типа компонента.
        
        Args:
            component: Тип компонента
            
        Returns:
            Промпт для компонента
        """
        component_name = component.value
        
        # Проверяем кэш
        if component_name in self._component_prompts_cache:
            return self._component_prompts_cache[component_name]
        
        # Определяем имя файла для компонента
        filename = f"{component_name}.txt"
        
        try:
            # Загружаем промпт из файла
            prompt = self._load_prompt_from_file(filename)
            self._component_prompts_cache[component_name] = prompt
            return prompt
        except FileNotFoundError:
            # Если файл не найден, возвращаем базовый промпт для фитингов
            if component_name == "fittings":
                # Возвращаем базовый промпт для фитингов
                base_prompt = """Ты специалист по гидравлическим фитингам.
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
                
                # Сохраняем базовый промпт в файл для будущего использования
                file_path = self.prompts_dir / filename
                file_path.write_text(base_prompt, encoding='utf-8')
                print(f"Создан базовый файл промпта для {component_name}: {file_path}")
                
                self._component_prompts_cache[component_name] = base_prompt
                return base_prompt
            else:
                # Для других компонентов возвращаем общий промпт
                fallback_prompt = f"""Ты специалист по гидравлическим компонентам типа {component_name}.
Проанализируй запрос и извлеки параметры компонента.

Верни результат строго в формате JSON.
Не добавляй пояснений, комментариев или дополнительного текста."""
                
                self._component_prompts_cache[component_name] = fallback_prompt
                return fallback_prompt
    
    def get_preprocessing_prompt(self, task: PreprocessingTask) -> str:
        """
        Получает промпт для задачи предобработки.
        
        Args:
            task: Задача предобработки
            
        Returns:
            Промпт для задачи предобработки
        """
        task_name = task.value
        
        # Проверяем кэш
        if task_name in self._preprocessing_prompts_cache:
            return self._preprocessing_prompts_cache[task_name]
        
        # Определяем имя файла для задачи предобработки
        filename = f"{task_name}.txt"
        
        try:
            # Загружаем промпт из файла
            prompt = self._load_prompt_from_file(filename)
            self._preprocessing_prompts_cache[task_name] = prompt
            return prompt
        except FileNotFoundError:
            # Возвращаем базовый промпт
            fallback_prompts = {
                "classify": "Определи тип гидравлического компонента. Ответь одним словом.",
                "quantity": "Извлеки количество компонентов из запроса. Ответь числом.",
                "split": "Раздели текст на отдельные позиции, по одной на строку."
            }
            
            fallback_prompt = fallback_prompts.get(task_name, "Обработай запрос.")
            self._preprocessing_prompts_cache[task_name] = fallback_prompt
            return fallback_prompt
    
    def save_component_prompt(self, component: ComponentType, prompt: str) -> None:
        """
        Сохраняет промпт для компонента в файл.
        
        Args:
            component: Тип компонента
            prompt: Промпт для сохранения
        """
        component_name = component.value
        filename = f"{component_name}.txt"
        file_path = self.prompts_dir / filename
        
        # Сохраняем промпт в файл
        file_path.write_text(prompt, encoding='utf-8')
        
        # Обновляем кэш
        self._component_prompts_cache[component_name] = prompt
        
        print(f"Промпт для {component_name} сохранен в: {file_path}")
    
    def save_preprocessing_prompt(self, task: PreprocessingTask, prompt: str) -> None:
        """
        Сохраняет промпт для задачи предобработки в файл.
        
        Args:
            task: Задача предобработки
            prompt: Промпт для сохранения
        """
        task_name = task.value
        filename = f"{task_name}.txt"
        file_path = self.prompts_dir / filename
        
        # Сохраняем промпт в файл
        file_path.write_text(prompt, encoding='utf-8')
        
        # Обновляем кэш
        self._preprocessing_prompts_cache[task_name] = prompt
        
        print(f"Промпт для {task_name} сохранен в: {file_path}")