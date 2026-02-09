from typing import Dict, Any
from datetime import datetime

from backend.ai.interfaces.ai_client import IAIClient
from backend.ai.interfaces.prompt_repository import IPromptRepository
from backend.ai.parser import AIResponseParser
from backend.ai.prompts.types import ComponentType, PreprocessingTask


class AIProcessingService:

    def __init__(
        self,
        client: IAIClient,
        prompts: IPromptRepository
    ):
        self.client = client
        self.prompts = prompts

    def process(self, query: str) -> Dict[str, Any]:
        ts = datetime.utcnow().isoformat()

        prompt = self.prompts.get_preprocessing_prompt(
            PreprocessingTask.CLASSIFY
        )
        raw_type = self.client.generate(prompt, query)

        comp_type = AIResponseParser.normalize_classification(
            raw_type or "",
            {t.value for t in ComponentType}
        )

        if not comp_type:
            return {"success": False, "error": "Unknown component", "timestamp": ts}

        data_prompt = self.prompts.get_component_prompt(
            ComponentType(comp_type)
        )
        params = self.client.extract_json(data_prompt, query)

        return {
            "success": True,
            "component_type": comp_type,
            "data": params,
            "timestamp": ts
        }
