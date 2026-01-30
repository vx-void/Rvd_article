# hydro_find/prompts/repository.py

from .types import ComponentType, PreprocessingTask
from .specs import (
    JSON_INSTRUCTION, EXTRACTION_RULES, PREPROCESSING_RULES,
    _FITTINGS_SPEC, _ADAPTERS_SPEC, _PLUGS_SPEC, _ADAPTER_TEE_SPEC,
    _BANJO_SPEC, _BANJO_BOLT_SPEC, _BRS_SPEC, _COUPLING_SPEC,
    _TEXT_SPLIT_SPEC, _QUANTITY_SPEC, _CLASSIFICATION_SPEC
)

# Сборка промпта
def _build_prompt(role: str, spec: str, is_json: bool = True) -> str:
    parts = [f"Ты {role}. {spec}"]
    if is_json:
        parts.extend([JSON_INSTRUCTION, EXTRACTION_RULES])
    else:
        parts.append(PREPROCESSING_RULES)
    return "\n\n".join(parts)

# Промпты компонентов
_COMPONENT_PROMPTS = {
    "fittings": _build_prompt("специалист по гидравлическим фитингам", _FITTINGS_SPEC),
    "adapters": _build_prompt("специалист по гидравлическим адаптерам", _ADAPTERS_SPEC),
    "plugs": _build_prompt("специалист по гидравлическим заглушкам", _PLUGS_SPEC),
    "adapter-tee": _build_prompt("специалист по гидравлическим адаптерам-тройникам", _ADAPTER_TEE_SPEC),
    "banjo": _build_prompt("специалист по гидравлическим банжо", _BANJO_SPEC),
    "banjo-bolt": _build_prompt("специалист по банжо-болтам", _BANJO_BOLT_SPEC),
    "brs": _build_prompt("специалист по БРС", _BRS_SPEC),
    "coupling": _build_prompt("специалист по муфтам", _COUPLING_SPEC),
}

# Промпты предобработки
_PREPROCESSING_PROMPTS = {
    "split": _build_prompt("ассистент по обработке технических текстов", _TEXT_SPLIT_SPEC, is_json=False),
    "quantity": _build_prompt("ассистент по обработке технических текстов", _QUANTITY_SPEC, is_json=False),
    "classify": _build_prompt("ассистент по обработке технических текстов", _CLASSIFICATION_SPEC, is_json=False),
}

# Публичный интерфейс
class PromptRepository:
    @staticmethod
    def get_component_prompt(component_type: ComponentType) -> str:
        prompt = _COMPONENT_PROMPTS.get(component_type.value)
        if not prompt:
            raise ValueError(f"Неизвестный тип компонента: {component_type}")
        return prompt

    @staticmethod
    def get_preprocessing_prompt(task: PreprocessingTask) -> str:
        prompt = _PREPROCESSING_PROMPTS.get(task.value)
        if not prompt:
            raise ValueError(f"Неизвестная задача предобработки: {task}")
        return prompt