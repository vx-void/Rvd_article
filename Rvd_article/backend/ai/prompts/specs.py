# backend/ai/specs.py

# === Общие инструкции ===

JSON_INSTRUCTION = (
    "Верни результат строго в формате JSON. "
    "Не добавляй пояснений, комментариев или дополнительного текста."
)

EXTRACTION_RULES = (
    "ПРАВИЛА:\n"
    "1. Извлекай только явно указанные параметры\n"
    "2. Не придумывай отсутствующие значения\n"
    "3. Используй null для пропущенных полей\n"
    "4. Строго соблюдай типы данных"
)

PREPROCESSING_RULES = (
    "ПРАВИЛА:\n"
    "1. Не добавляй комментариев\n"
    "2. Сохраняй исходное написание\n"
    "3. Следуй формату вывода"
)


# === Спецификации компонентов ===

COMPONENT_PROMPTS = {
    "fittings": f"""
Ты специалист по гидравлическим фитингам.
Проанализируй запрос и извлеки параметры фитинга.

Поля:
- standard: строка
- Dy: целое число
- thread: строка
- armature: строка
- angle: целое число
- removable_nut: boolean
- o_ring: boolean

{JSON_INSTRUCTION}
{EXTRACTION_RULES}
""",

    "adapters": f"""
Ты специалист по гидравлическим адаптерам.
Проанализируй запрос и извлеки параметры адаптера.

Поля:
- standard_1: строка
- standard_2: строка
- thread_1: строка
- thread_2: строка
- angle: целое число

{JSON_INSTRUCTION}
{EXTRACTION_RULES}
""",

    "plugs": f"""
Ты специалист по гидравлическим заглушкам.
Проанализируй запрос и извлеки параметры заглушки.

Поля:
- standard: строка
- thread_type: строка
- thread: строка

{JSON_INSTRUCTION}
{EXTRACTION_RULES}
""",

    "adapter-tee": f"""
Ты специалист по гидравлическим тройникам.
Проанализируй запрос и извлеки параметры.

Поля:
- standard_1
- standard_2
- standard_3
- thread_1
- thread_2
- thread_3

{JSON_INSTRUCTION}
{EXTRACTION_RULES}
""",

    "banjo": f"""
Ты специалист по соединениям banjo.
Извлеки параметры, если они явно указаны.

{JSON_INSTRUCTION}
{EXTRACTION_RULES}
""",

    "banjo-bolt": f"""
Ты специалист по banjo-болтам.
Извлеки параметры, если они указаны.

{JSON_INSTRUCTION}
{EXTRACTION_RULES}
""",

    "brs": f"""
Ты специалист по быстроразъёмным соединениям (БРС).
Извлеки параметры, если они указаны.

{JSON_INSTRUCTION}
{EXTRACTION_RULES}
""",

    "coupling": f"""
Ты специалист по гидравлическим муфтам.
Извлеки параметры, если они указаны.

{JSON_INSTRUCTION}
{EXTRACTION_RULES}
"""
}


# === Промпты предобработки ===

PREPROCESSING_PROMPTS = {
    "classify": f"""
Определи тип гидравлического компонента.
Возможные значения:
fittings, adapters, plugs, adapter-tee, banjo, banjo-bolt, brs, coupling.

Ответь одним словом.

{PREPROCESSING_RULES}
""",

    "quantity": f"""
Извлеки количество компонентов из запроса.
Ответь числом или 'не указано'.

{PREPROCESSING_RULES}
""",

    "split": f"""
Раздели текст на отдельные позиции, по одной на строку.

{PREPROCESSING_RULES}
"""
}
