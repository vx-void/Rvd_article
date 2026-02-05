#../interfaces/prompt_repository.py
from abc import ABC, abstractmethod
from backend.ai.types import ComponentType, PreprocessingTask


class PromptRepositoryInterface(ABC):

    @abstractmethod
    def get_component_prompt(self, component: ComponentType) -> str:
        pass

    @abstractmethod
    def get_preprocessing_prompt(self, task: PreprocessingTask) -> str:
        pass
