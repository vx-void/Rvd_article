# hydro_find/prompts/components.py

from .base import PromptRole, build_prompt

_FITTINGS_SPEC = """Проанализируй запрос и извлеки параметры фитинга.

ПОЛЯ:
- standard: строка (DKOL, DKOS, NPTF, BSP, JIC и т.д.)
- Dy: целое число
- thread: строка
- armature: "штуцер", "штуцер конусный", "гайка"
- angle: целое число (0, 45, 90)
- removable_nut: boolean
- unstandard_thread: boolean
- D_out: целое число (только если указано)
- usit: boolean
- s_key: строка (только если указан)
- compact: boolean
- pin: boolean
- o_ring: boolean
- long: целое число"""

# Аналогично для других типов...
_ADAPTERS_SPEC = """Проанализируй запрос и извлеки параметры адаптера.

ПОЛЯ:
- standard_1, standard_2: строки
- thread_1, thread_2: строки
- armature_1, armature_2: "штуцер", "штуцер конусный", "гайка" (только если указано)
- angle: целое число
- s_key: строка (только если указан)"""

_PLUGS_SPEC = """Проанализируй запрос и извлеки параметры заглушки.

ПОЛЯ:
- standard: строка
- thread_type: "метрическая" или "дюймовая"
- thread: строка
- armature: "штуцер" или "гайка" (только если указано)
- s_key: строка (только если указан)"""

_ADAPTER_TEE_SPEC = """Проанализируй запрос и извлеки параметры адаптера-тройника.

ПОЛЯ:
- standard_1, standard_2, standard_3: строки
- thread_1, thread_2, thread_3: строки
- armature_1, armature_2, armature_3: "гайка", "штуцер", "штуцер конусный" (только если указано)"""

# Экспорт
COMPONENT_PROMPTS = {
    "fittings": build_prompt(PromptRole.COMPONENT_EXTRACTOR, _FITTINGS_SPEC),
    "adapters": build_prompt(PromptRole.COMPONENT_EXTRACTOR, _ADAPTERS_SPEC),
    "plugs": build_prompt(PromptRole.COMPONENT_EXTRACTOR, _PLUGS_SPEC),
    "adapter-tee": build_prompt(PromptRole.COMPONENT_EXTRACTOR, _ADAPTER_TEE_SPEC),
}