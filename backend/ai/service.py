import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from backend.ai.client import OpenRouterClient
from backend.ai.prompts import (
    ComponentType,
    PreprocessingTask,
    PromptRepository
)

logger = logging.getLogger(__name__)


class AIProcessingService:
    def __init__(self):
        try:
            self.client = OpenRouterClient()
            logger.info("AIProcessingService инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации AIProcessingService: {e}")
            raise

    def _classify(self, query: str) -> Optional[str]:
        """Классификация типа компонента"""
        logger.debug(f"Классификация запроса: {query[:50]}...")

        prompt = PromptRepository.get_preprocessing_prompt(PreprocessingTask.CLASSIFY)
        response = self.client.generate(prompt, query)

        if not response:
            logger.warning("Не удалось классифицировать запрос: AI не ответил")
            return None

        # Очистка ответа
        raw = response.lower().strip().strip('"\'').strip('`')
        logger.debug(f"Ответ классификации: {raw}")

        # Проверка на допустимые типы
        allowed = {t.value for t in ComponentType}
        if raw in allowed:
            logger.info(f"Запрос классифицирован как: {raw}")
            return raw
        else:
            logger.warning(f"Недопустимый тип компонента в ответе AI: {raw}")
            # Попробуем найти подходящий тип
            for allowed_type in allowed:
                if allowed_type in raw or raw in allowed_type:
                    logger.info(f"Использую тип из частичного совпадения: {allowed_type}")
                    return allowed_type
            return None

    def _extract_params(self, query: str, component_type: str) -> Optional[Dict[str, Any]]:
        """Извлечение параметров компонента"""
        logger.debug(f"Извлечение параметров для {component_type}: {query[:50]}...")

        try:
            prompt = PromptRepository.get_component_prompt(ComponentType(component_type))
            result = self.client.extract_json(prompt, query)

            if result:
                logger.info(f"Параметры извлечены для {component_type}, ключи: {list(result.keys())}")
            else:
                logger.warning(f"Не удалось извлечь параметры для {component_type}")

            return result

        except ValueError as e:
            logger.error(f"Неизвестный тип компонента для извлечения параметров: {component_type}")
            return None
        except Exception as e:
            logger.exception(f"Ошибка извлечения параметров: {e}")
            return None

    def _extract_quantity(self, text: str) -> Optional[int]:
        """Извлечение количества"""
        logger.debug(f"Извлечение количества из: {text[:50]}...")

        prompt = PromptRepository.get_preprocessing_prompt(PreprocessingTask.QUANTITY)
        response = self.client.generate(prompt, text)

        if not response:
            logger.debug("Не удалось извлечь количество: AI не ответил")
            return None

        response = response.strip()
        if response.lower() == "не указано" or not response:
            logger.debug("Количество не указано в запросе")
            return None

        # Извлечение цифр
        digits = ''.join(filter(str.isdigit, response))
        if digits:
            quantity = int(digits)
            logger.debug(f"Извлечено количество: {quantity}")
            return quantity
        else:
            logger.debug(f"Не удалось извлечь количество из ответа: {response}")
            return None

    def _split_batch(self, text: str) -> List[str]:
        """Разделение пакетного запроса на отдельные строки"""
        logger.debug(f"Разделение пакетного запроса")

        prompt = PromptRepository.get_preprocessing_prompt(PreprocessingTask.SPLIT)
        response = self.client.generate(prompt, text)

        if not response:
            logger.warning("Не удалось разделить пакетный запрос: AI не ответил")
            # Возвращаем как одну строку
            return [text.strip()] if text.strip() else []

        lines = response.strip().split('\n')
        result = [line.strip() for line in lines if line.strip()]

        logger.info(f"Пакетный запрос разделен на {len(result)} строк")
        return result

    def process_single(self, query: str) -> Dict[str, Any]:
        """Обработка одного запроса"""
        ts = datetime.now().isoformat()

        logger.info(f"Начало обработки AI запроса: {query[:100]}...")

        try:
            # 1. Классификация
            comp_type = self._classify(query)
            logger.info(f"[AI Service] component_type: '{comp_type}'")
            if not comp_type:
                logger.warning("Не удалось определить тип компонента")
                return self._error("Не удалось определить тип компонента", ts)

            # 2. Извлечение параметров
            params = self._extract_params(query, comp_type)
            if not params:
                logger.warning("Не удалось извлечь параметры")
                return self._error("Не удалось извлечь параметры", ts)

            # 3. Извлечение количества
            qty = self._extract_quantity(query)

            result = {
                "success": True,
                "component_type": comp_type,
                "original_query": query,
                "extracted_data": params,
                "quantity": qty,
                "timestamp": ts
            }

            logger.info(f"AI запрос успешно обработан. Тип: {comp_type}")

            return result

        except Exception as e:
            logger.exception(f"Ошибка обработки AI запроса: {e}")
            return self._error(f"Ошибка ИИ: {e}", ts)

    def process_batch(self, text: str) -> Dict[str, Any]:
        """Пакетная обработка"""
        ts = datetime.now().isoformat()

        logger.info(f"Начало пакетной AI обработки")

        try:
            # Разделение на строки
            lines = self._split_batch(text)
            if not lines:
                return self._error("Не удалось разделить текст на строки", ts)

            # Обработка каждой строки
            results = []
            for i, line in enumerate(lines, 1):
                logger.debug(f"Обработка строки {i}/{len(lines)}: {line[:50]}...")
                result = self.process_single(line)
                results.append(result)

            batch_result = {
                "success": True,
                "batch": True,
                "results": results,
                "total_items": len(lines),
                "processed_items": len([r for r in results if r.get("success")]),
                "timestamp": ts
            }

            logger.info(f"Пакетная AI обработка завершена: {batch_result['processed_items']}/{len(lines)} успешно")

            return batch_result

        except Exception as e:
            logger.exception(f"Ошибка пакетной AI обработки: {e}")
            return self._error(f"Ошибка пакетной обработки: {e}", ts)

    @staticmethod
    def _error(msg: str, ts: str) -> Dict[str, Any]:
        """Формирование ответа об ошибке"""
        error_result = {
            "success": False,
            "error": msg,
            "timestamp": ts
        }
        logger.error(f"AI обработка завершилась ошибкой: {msg}")
        return error_result

    def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья AI сервиса"""
        try:
            # Простой тестовый запрос
            test_query = "гидравлический фитинг 1/2 BSP"
            result = self._classify(test_query)

            if result:
                return {
                    "status": "healthy",
                    "ai_service": "operational",
                    "model": self.client.model,
                    "test_query": test_query,
                    "test_result": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "degraded",
                    "ai_service": "responding_but_error",
                    "model": self.client.model,
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "ai_service": "down",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }