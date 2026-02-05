from backend.ai.interfaces.prompt_repository import PromptRepositoryInterface
from backend.ai.types import ComponentType, PreprocessingTask
from backend.ai.specs import (
    COMPONENT_PROMPTS,
    PREPROCESSING_PROMPTS
)


class PromptRepository(PromptRepositoryInterface):

    def get_component_prompt(self, component: ComponentType) -> str:
        return COMPONENT_PROMPTS[component.value]

    def get_preprocessing_prompt(self, task: PreprocessingTask) -> str:
        return PREPROCESSING_PROMPTS[task.value]
