from ai.interfaces.prompt_repository import IPromptRepository
from ai.prompts.types import ComponentType, PreprocessingTask
from ai.prompts.specs import (
    COMPONENT_PROMPTS,
    PREPROCESSING_PROMPTS
)


class PromptRepository(IPromptRepository):

    def get_component_prompt(self, component: ComponentType) -> str:
        return COMPONENT_PROMPTS[component.value]

    def get_preprocessing_prompt(self, task: PreprocessingTask) -> str:
        return PREPROCESSING_PROMPTS[task.value]
