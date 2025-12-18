# hydro_find/prompts/base.py

from enum import Enum


class PromptRole(Enum):
    COMPONENT_EXTRACTOR = "специалист по гидравлическим компонентам"
    TEXT_PREPROCESSOR = "ассистент по обработке технических текстов"


class PromptSection(Enum):
    JSON_INSTRUCTION = (
        "Верни результат В СТРОГОМ ФОРМАТЕ JSON.\n"
        "Не включай пояснений, комментариев или дополнительного текста."
    )
    EXTRACTION_RULES = (
        "ПРАВИЛА:\n"
        "1. Извлекай ТОЛЬКО явно указанные параметры\n"
        "2. Не придумывай отсутствующие поля\n"
        "3. Используй null для пропущенных значений\n"
        "4. Соблюдай типы: boolean, integer, string"
    )
    PREPROCESSING_RULES = (
        "ПРАВИЛА:\n"
        "1. Сохраняй оригинальное написание компонентов\n"
        "2. Не добавляй пояснений\n"
        "3. Строго следуй формату вывода"
    )


def build_prompt(role: PromptRole, task_spec: str, is_json: bool = True) -> str:
    """Универсальный конструктор промптов."""
    parts = [f"Ты {role.value}. {task_spec}"]
    if is_json:
        parts.extend([PromptSection.JSON_INSTRUCTION.value, PromptSection.EXTRACTION_RULES.value])
    else:
        parts.append(PromptSection.PREPROCESSING_RULES.value)
    return "\n\n".join(parts)