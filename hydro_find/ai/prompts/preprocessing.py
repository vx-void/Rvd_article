# hydro_find/prompts/preprocessing.py

from .base import PromptRole, build_prompt

TEXT_SPLIT_SPEC = """Тебе предоставлена одна строка с перечнем компонентов.
Разбей её на отдельные строки — по одному компоненту на строку.
Каждая строка должна содержать полное описание компонента и количество (если есть).

Пример:
Ввод: "Муфта... - 100шт Прокладка... - 200шт"
Вывод:
Муфта... - 100шт
Прокладка... - 200шт"""

QUANTITY_EXTRACT_SPEC = """Извлеки количество компонентов из строки.
Верни ТОЛЬКО первое число или "Не указано", если цифр нет."""

# Эти промпты НЕ возвращают JSON — отключаем JSON-режим
TEXT_SPLIT_PROMPT = build_prompt(
    PromptRole.TEXT_PREPROCESSOR,
    TEXT_SPLIT_SPEC,
    is_json=False
)

QUANTITY_EXTRACT_PROMPT = build_prompt(
    PromptRole.TEXT_PREPROCESSOR,
    QUANTITY_EXTRACT_SPEC,
    is_json=False
)


CLASSIFICATION_SPEC = """Ты классификатор гидравлических компонентов.
Проанализируй ввод и верни ОДНО из значений:

- fittings
- adapters
- plugs
- adapter-tee
- banjo
- banjo-bolt
- brs
- coupling

ПРАВИЛА:
1. Возвращай ТОЛЬКО одно значение из списка выше
2. Не добавляй пояснений, описаний или дополнительного текста
3. Если тип не определяется — возвращай "unknown\""""

CLASSIFICATION_PROMPT = build_prompt(
    PromptRole.TEXT_PREPROCESSOR,
    CLASSIFICATION_SPEC,
    is_json=False
)