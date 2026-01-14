import hashlib
import logging
import time
import traceback
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Структурированный результат обработки сообщения"""
    task_id: str
    status: str  # 'completed', 'error', 'partial', 'cached'
    query: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    cached: bool = False
    partial: bool = False
    processing_time: Optional[float] = None
    timestamp: Optional[float] = None

    def __post_init__(self):
        """Инициализация после создания датакласса"""
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return asdict(self)


class RMQWorker:
    """Worker для обработки сообщений из RabbitMQ"""

    def __init__(
            self,
            ai_service=None,
            db_service=None,
            cache_service=None,
            cache_ttl: int = 3600,  # 1 час
            enable_cache: bool = True,
            enable_partial_results: bool = True
    ):
        """
        Инициализация worker'а.

        Args:
            ai_service: Сервис ИИ обработки
            db_service: Сервис работы с БД
            cache_service: Сервис кэширования
            cache_ttl: Время жизни кэша в секундах
            enable_cache: Включить кэширование
            enable_partial_results: Возвращать частичные результаты при ошибках
        """
        self.cache_ttl = cache_ttl
        self.enable_cache = enable_cache
        self.enable_partial_results = enable_partial_results

        # Инициализация сервисов
        self._init_services(ai_service, db_service, cache_service)

        logger.info("RMQWorker инициализирован")

    def _init_services(self, ai_service, db_service, cache_service):
        """Инициализация сервисов"""
        # AI Service - ОБЯЗАТЕЛЬНО должен быть передан или создан
        if ai_service is None:
            try:
                from backend.services.ai_service import AIService
                self._ai_service = AIService()
                logger.info("AI сервис создан")
            except ImportError as e:
                logger.error(f"Ошибка импорта AI сервиса: {e}")
                raise
            except Exception as e:
                logger.error(f"Ошибка создания AI сервиса: {e}")
                raise
        else:
            self._ai_service = ai_service
            logger.info("AI сервис передан извне")

        # DB Service
        if db_service is None:
            try:
                from backend.services.db_service import DBService
                self._db_service = DBService()
                logger.info("DB сервис создан")
            except ImportError as e:
                logger.error(f"Ошибка импорта DB сервиса: {e}")
                # Не падаем, так как возможна работа без БД
                self._db_service = None
            except Exception as e:
                logger.error(f"Ошибка создания DB сервиса: {e}")
                self._db_service = None
        else:
            self._db_service = db_service

        # Cache Service
        if cache_service is None:
            try:
                from backend.services.cache_service import CacheService
                self._cache_service = CacheService()
                logger.info("Cache сервис создан")
            except ImportError as e:
                logger.error(f"Ошибка импорта Cache сервиса: {e}")
                # Не падаем, так как возможна работа без кэша
                self._cache_service = None
            except Exception as e:
                logger.error(f"Ошибка создания Cache сервиса: {e}")
                self._cache_service = None
        else:
            self._cache_service = cache_service

    @property
    def ai(self):
        """Геттер для AI сервиса"""
        if self._ai_service is None:
            raise RuntimeError("AI сервис не инициализирован")
        return self._ai_service

    @property
    def db(self):
        """Геттер для DB сервиса"""
        if self._db_service is None:
            raise RuntimeError("DB сервис не инициализирован")
        return self._db_service

    @property
    def cache(self):
        """Геттер для Cache сервиса"""
        if self._cache_service is None:
            raise RuntimeError("Cache сервис не инициализирован")
        return self._cache_service

    def _generate_cache_key(self, query: str, **kwargs) -> str:
        """Генерация ключа кэша"""
        base_string = query + json.dumps(kwargs, sort_keys=True)
        return f"search:{hashlib.sha256(base_string.encode()).hexdigest()}"

    def _validate_message(self, message: Dict[str, Any]) -> Optional[str]:
        """Валидация входящего сообщения"""
        if not isinstance(message, dict):
            return "Сообщение должно быть словарем"

        # Проверка обязательных полей
        required_fields = ['task_id', 'query']
        for field in required_fields:
            if field not in message:
                return f"Отсутствует обязательное поле: {field}"

        # Проверка типов
        if not isinstance(message['task_id'], str):
            return "task_id должен быть строкой"

        if not isinstance(message['query'], str):
            return "query должен быть строкой"

        # Проверка content
        query = message['query'].strip()
        if not query:
            return "query не может быть пустым"

        return None

    def _get_cached_result(self, query: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Получение результата из кэша"""
        if not self.enable_cache or self._cache_service is None:
            return None

        try:
            cache_key = self._generate_cache_key(query, **kwargs)
            cached_result = self.cache.get_cached_search_result(cache_key)

            if cached_result:
                logger.debug(f"Кэш попадание для запроса: {query[:50]}...")
                return cached_result

        except Exception as e:
            logger.warning(f"Ошибка доступа к кэшу: {e}")

        return None

    def _save_to_cache(self, query: str, result: Dict[str, Any], **kwargs):
        """Сохранение результата в кэш"""
        if not self.enable_cache or self._cache_service is None:
            return

        try:
            cache_key = self._generate_cache_key(query, **kwargs)
            self.cache.cache_search_result(cache_key, result, ttl=self.cache_ttl)
            logger.debug(f"Результат сохранен в кэш")

        except Exception as e:
            logger.error(f"Ошибка сохранения в кэш: {e}")

    def _process_ai_query(self, query: str) -> Dict[str, Any]:
        """Обработка запроса с помощью AI"""
        try:
            logger.info(f"Отправка запроса к AI: {query[:100]}...")

            # Вызываем AI сервис
            ai_result = self.ai.process_single(query)

            if not ai_result.get("success", False):
                error_msg = ai_result.get("error", "AI обработка не удалась")
                logger.error(f"AI обработка не удалась: {error_msg}")

                # Определяем тип ошибки
                error_lower = error_msg.lower()

                # Если AI не смог определить тип компонента
                if 'не удалось определить тип компонента' in error_lower:
                    raise ValueError("AI не смог определить тип компонента")
                else:
                    raise RuntimeError(f"AI сервис ошибка: {error_msg}")

            logger.info(f"AI обработка завершена успешно. Тип: {ai_result.get('component_type')}")
            return ai_result

        except ValueError as e:
            # Это ошибка "не удалось определить тип компонента" - прокидываем дальше
            raise
        except Exception as e:
            logger.exception(f"Исключение в AI обработке: {e}")
            raise

    def _search_database(self, ai_result: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Поиск в базе данных"""
        if self._db_service is None:
            logger.warning("DB сервис недоступен, пропускаем поиск в БД")
            return []

        try:
            search_params = {
                "component_type": ai_result.get("component_type", ""),
                "original_query": query,
                **ai_result.get("extracted_data", {})
            }

            logger.debug(f"Поиск в БД с параметрами: {search_params}")
            matches = self.db.search_by_ai_params(search_params)

            return matches

        except Exception as e:
            logger.exception(f"Ошибка поиска в БД: {e}")
            return []

    def _prepare_final_result(
            self,
            query: str,
            ai_result: Dict[str, Any],
            matches: List[Dict[str, Any]],
            db_error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Подготовка финального результата"""
        result = {
            "query": query,
            "source": "database" if matches and not db_error else "ai_only",
            "matches": matches,
            "match_count": len(matches),
            "ai_result": {
                "component_type": ai_result.get("component_type"),
                "extracted_data": ai_result.get("extracted_data", {}),
                "confidence": ai_result.get("confidence", 0.0),
                "success": ai_result.get("success", True)
            },
            "timestamp": time.time()
        }

        if db_error:
            result["db_error"] = db_error
            result["partial"] = True

        return result

    def _update_task_status(self, task_id: str, status: str, data: Dict[str, Any]):
        """Обновление статуса задачи в кэше"""
        if self._cache_service is None:
            return

        try:
            self.cache.set_task_status(task_id, status, data)
            logger.debug(f"Статус задачи {task_id} обновлен: {status}")
        except Exception as e:
            logger.warning(f"Не удалось обновить статус задачи {task_id}: {e}")

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Основной метод обработки сообщения.

        Args:
            message: Входящее сообщение из RabbitMQ

        Returns:
            Dict: Результат обработки
        """
        start_time = time.time()
        task_id = message.get('task_id', 'unknown')
        query = message.get('query', '').strip()

        # Создаем контекст для логгирования
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.task_id = task_id
            return record

        logging.setLogRecordFactory(record_factory)

        try:
            logger.info(f"Начало обработки задачи")

            # 1. Валидация сообщения
            validation_error = self._validate_message(message)
            if validation_error:
                error_msg = f"Ошибка валидации: {validation_error}"
                logger.error(error_msg)

                result = ProcessingResult(
                    task_id=task_id,
                    status='error',
                    query=query,
                    error=error_msg,
                    processing_time=time.time() - start_time
                )

                if self._cache_service:
                    self._update_task_status(task_id, 'error', {"error": error_msg})
                return result.to_dict()

            # 2. Проверка кэша
            cached_result = self._get_cached_result(query)
            if cached_result:
                logger.info(f"Результат найден в кэше")

                result = ProcessingResult(
                    task_id=task_id,
                    status='completed',
                    query=query,
                    result=cached_result,
                    cached=True,
                    processing_time=time.time() - start_time
                )

                if self._cache_service:
                    self._update_task_status(task_id, 'completed', cached_result)
                return result.to_dict()

            # 3. Обработка AI
            logger.info(f"Отправка запроса к AI сервису...")
            try:
                ai_result = self._process_ai_query(query)
                logger.info(f"AI обработка завершена: {ai_result.get('component_type')}")

            except Exception as e:
                error_msg = f"AI обработка не удалась: {str(e)}"
                logger.error(error_msg)

                result = ProcessingResult(
                    task_id=task_id,
                    status='error',
                    query=query,
                    error=error_msg,
                    processing_time=time.time() - start_time
                )

                if self._cache_service:
                    self._update_task_status(task_id, 'error', {"error": error_msg})
                return result.to_dict()

            # 4. Поиск в БД
            db_error = None
            try:
                matches = self._search_database(ai_result, query)
                logger.info(f"Найдено {len(matches)} совпадений в БД")

            except Exception as e:
                db_error = f"Ошибка поиска в БД: {str(e)}"
                matches = []
                logger.error(db_error)

            # 5. Подготовка результата
            final_result = self._prepare_final_result(query, ai_result, matches, db_error)

            # 6. Сохранение в кэш (только если нет ошибки БД)
            if db_error is None:
                self._save_to_cache(query, final_result)

            # 7. Определение статуса результата
            status = 'completed'
            partial = False

            if db_error and self.enable_partial_results:
                status = 'partial'
                partial = True
                logger.warning(f"Частичный результат из-за ошибки БД: {db_error}")

            # 8. Обновление статуса задачи
            self._update_task_status(task_id, status, final_result)

            # 9. Возврат результата
            processing_time = time.time() - start_time
            logger.info(f"Обработка завершена за {processing_time:.2f} секунд")

            result = ProcessingResult(
                task_id=task_id,
                status=status,
                query=query,
                result=final_result,
                partial=partial,
                processing_time=processing_time
            )

            return result.to_dict()

        except Exception as e:
            error_msg = f"Неожиданная ошибка: {str(e)}"
            logger.exception(f"Неожиданная ошибка обработки: {e}")

            result = ProcessingResult(
                task_id=task_id,
                status='error',
                query=query,
                error=error_msg,
                processing_time=time.time() - start_time
            )

            if self._cache_service:
                try:
                    self._update_task_status(task_id, 'error', {"error": error_msg})
                except:
                    pass

            return result.to_dict()

        finally:
            # Восстанавливаем factory по умолчанию
            logging.setLogRecordFactory(old_factory)

    def health_check(self) -> Dict[str, Any]:
        """
        Проверка здоровья worker'а и его зависимостей.

        Returns:
            Dict: Статус здоровья всех компонентов
        """
        health = {
            "worker": "unknown",
            "timestamp": time.time(),
            "dependencies": {},
            "cache_enabled": self.enable_cache
        }

        # Проверка AI сервиса
        try:
            test_result = self.ai.process_single("тестовый фитинг 1/2 BSP")
            health["dependencies"]["ai_service"] = {
                "status": "ok" if test_result.get("success") else "error",
                "response_time": "tested",
                "model": "available"
            }
        except Exception as e:
            health["dependencies"]["ai_service"] = {
                "status": "error",
                "error": str(e)
            }

        # Проверка DB сервиса
        try:
            if self._db_service:
                # Простая проверка
                health["dependencies"]["db_service"] = {
                    "status": "ok",
                    "details": "connected"
                }
            else:
                health["dependencies"]["db_service"] = {
                    "status": "disabled",
                    "details": "service_not_initialized"
                }
        except Exception as e:
            health["dependencies"]["db_service"] = {
                "status": "error",
                "error": str(e)
            }

        # Проверка Cache сервиса
        try:
            if self._cache_service:
                # Простая проверка
                health["dependencies"]["cache_service"] = {
                    "status": "ok",
                    "details": "connected"
                }
            else:
                health["dependencies"]["cache_service"] = {
                    "status": "disabled",
                    "details": "service_not_initialized"
                }
        except Exception as e:
            health["dependencies"]["cache_service"] = {
                "status": "error",
                "error": str(e)
            }

        # Определение общего статуса
        ai_ok = health["dependencies"]["ai_service"]["status"] == "ok"
        all_ok = ai_ok  # AI - критически важная зависимость

        if all_ok:
            health["status"] = "healthy"
            health["worker"] = "ok"
        elif ai_ok:
            health["status"] = "degraded"
            health["worker"] = "ok"
        else:
            health["status"] = "unhealthy"
            health["worker"] = "error"

        return health