#../interfaces/prompt_repository.py
from abc import ABC, abstractmethod
from ai.prompts.types import ComponentType, PreprocessingTask


class IPromptRepository(ABC):

    @abstractmethod
    def get_component_prompt(self, component: ComponentType) -> str:
        pass

    @abstractmethod
    def get_preprocessing_prompt(self, task: PreprocessingTask) -> str:
        pass
