# hydro_find/prompts/registry.py

from typing import Literal, Union
from .components import COMPONENT_PROMPTS
from .preprocessing import TEXT_SPLIT_PROMPT, QUANTITY_EXTRACT_PROMPT, CLASSIFICATION_PROMPT


def get_component_prompt(component_type: str) -> str:
    """Возвращает промпт для извлечения параметров компонента."""
    if prompt := COMPONENT_PROMPTS.get(component_type):
        return prompt
    raise ValueError(f"Неизвестный тип компонента: {component_type}")


def get_preprocessing_prompt(task: Literal["split", "quantity"]) -> str:
    """Возвращает промпт для предобработки текста."""
    if task == "split":
        return TEXT_SPLIT_PROMPT
    elif task == "quantity":
        return QUANTITY_EXTRACT_PROMPT
    elif task == "classify":
        return CLASSIFICATION_PROMPT
    else:
        raise ValueError(f"Неизвестная задача: {task}")