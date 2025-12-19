# hydro_find/ai/service.py

from typing import Optional, Dict, Any, List
from datetime import datetime
from hydro_find.ai.client import OpenRouterClient
from hydro_find.prompts import (
    ComponentType,
    PreprocessingTask,
    PromptRepository
)

class AIProcessingService:
    def __init__(self):
        self.client = OpenRouterClient()

    def _classify(self, query: str) -> Optional[str]:
        prompt = PromptRepository.get_preprocessing_prompt(PreprocessingTask.CLASSIFY)
        response = self.client.generate(prompt, query)
        if response:
            raw = response.lower().strip().strip('"\'')
            allowed = {t.value for t in ComponentType}
            return raw if raw in allowed else None
        return None

    def _extract_params(self, query: str, component_type: str) -> Optional[Dict[str, Any]]:
        prompt = PromptRepository.get_component_prompt(ComponentType(component_type))
        return self.client.extract_json(prompt, query)

    def _extract_quantity(self, text: str) -> Optional[int]:
        prompt = PromptRepository.get_preprocessing_prompt(PreprocessingTask.QUANTITY)
        response = self.client.generate(prompt, text)
        if response and response.strip() != "Не указано":
            digits = ''.join(filter(str.isdigit, response))
            return int(digits) if digits else None
        return None

    def _split_batch(self, text: str) -> List[str]:
        prompt = PromptRepository.get_preprocessing_prompt(PreprocessingTask.SPLIT)
        response = self.client.generate(prompt, text)
        lines = (response or text).strip().split('\n')
        return [line.strip() for line in lines if line.strip()]

    def process_single(self, query: str) -> Dict[str, Any]:
        ts = datetime.now().isoformat()
        try:
            comp_type = self._classify(query)
            if not comp_type:
                return self._error("Не удалось определить тип компонента", ts)

            params = self._extract_params(query, comp_type)
            if not params:
                return self._error("Не удалось извлечь параметры", ts)

            qty = self._extract_quantity(query)

            return {
                "success": True,
                "component_type": comp_type,
                "original_query": query,
                "extracted_data": params,
                "quantity": qty,
                "timestamp": ts
            }
        except Exception as e:
            return self._error(f"Ошибка ИИ: {e}", ts)

    def process_batch(self, text: str) -> Dict[str, Any]:
        ts = datetime.now().isoformat()
        try:
            lines = self._split_batch(text)
            results = [self.process_single(line) for line in lines]
            return {
                "success": True,
                "batch": True,
                "results": results,
                "total_items": len(lines),
                "timestamp": ts
            }
        except Exception as e:
            return self._error(f"Ошибка пакетной обработки: {e}", ts)

    def _error(self, msg: str, ts: str) -> Dict[str, Any]:
        return {"success": False, "error": msg, "timestamp": ts}