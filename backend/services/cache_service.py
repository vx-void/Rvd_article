import redis
import json
import os
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class CacheService:
    """Сервис кэширования с использованием Redis"""

    def __init__(
            self,
            host: Optional[str] = None,
            port: Optional[int] = None,
            db: int = 0,
            decode_responses: bool = True,
            max_connections: int = 10
    ):
        """
        Инициализация Redis клиента.

        Args:
            host: Хост Redis (по умолчанию из env REDIS_HOST или localhost)
            port: Порт Redis (по умолчанию из env REDIS_PORT или 6379)
            db: Номер базы данных Redis
            decode_responses: Декодировать ответы в строки
            max_connections: Максимальное количество соединений в пуле
        """
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", 6379))
        self.db = db
        self.decode_responses = decode_responses

        try:
            # Используем ConnectionPool для лучшей производительности
            self.connection_pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=decode_responses,
                max_connections=max_connections,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )

            self._redis = redis.Redis(connection_pool=self.connection_pool)

            # Проверяем подключение
            self._redis.ping()
            logger.info(f"Успешно подключено к Redis {self.host}:{self.port} (db:{self.db})")

        except redis.exceptions.ConnectionError as e:
            logger.error(f"Ошибка подключения к Redis {self.host}:{self.port}: {e}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при подключении к Redis: {e}")
            raise

    def set_task_status(
            self,
            task_id: str,
            status: str,
            result: Optional[Dict[str, Any]] = None,
            ttl: int = 3600
    ) -> bool:
        """
        Сохранение статуса задачи.

        Args:
            task_id: Идентификатор задачи
            status: Статус задачи (processing, completed, error)
            result: Результат обработки
            ttl: Время жизни в секундах

        Returns:
            bool: Успешность операции
        """
        try:
            key = f"task:{task_id}"
            value = {
                "status": status,
                "result": result,
                "updated_at": datetime.now().isoformat(),
                "ttl": ttl
            }

            success = self._redis.setex(key, ttl, json.dumps(value))

            if success:
                logger.debug(f"Статус задачи сохранен", extra={
                    'task_id': task_id,
                    'status': status,
                    'ttl': ttl
                })
            else:
                logger.error(f"Не удалось сохранить статус задачи", extra={'task_id': task_id})

            return bool(success)

        except Exception as e:
            logger.exception(f"Ошибка сохранения статуса задачи {task_id}: {e}")
            return False

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение статуса задачи.

        Args:
            task_id: Идентификатор задачи

        Returns:
            Optional[Dict]: Статус и результат задачи
        """
        try:
            key = f"task:{task_id}"
            data = self._redis.get(key)

            if data:
                result = json.loads(data)

                # Обновляем TTL при каждом чтении (реализация sliding expiration)
                remaining_ttl = self._redis.ttl(key)
                if remaining_ttl > 0:
                    # Продлеваем TTL только если он еще не истек
                    new_ttl = min(3600, remaining_ttl + 300)  # Добавляем 5 минут, но не более часа
                    self._redis.expire(key, new_ttl)

                return result
            return None

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON для задачи {task_id}: {e}")
            return None
        except Exception as e:
            logger.exception(f"Ошибка получения статуса задачи {task_id}: {e}")
            return None

    def cache_search_result(
            self,
            query_hash: str,
            result: List[Dict[str, Any]],
            ttl: int = 600
    ) -> bool:
        """
        Кэширование результата поиска.

        Args:
            query_hash: Хэш запроса
            result: Результат поиска
            ttl: Время жизни в секундах

        Returns:
            bool: Успешность операции
        """
        try:
            key = f"search:{query_hash}"
            value = {
                "result": result,
                "cached_at": datetime.now().isoformat(),
                "result_count": len(result)
            }

            success = self._redis.setex(key, ttl, json.dumps(value))

            if success:
                logger.debug(f"Результат поиска закэширован", extra={
                    'query_hash': query_hash[:16],  # Только первые 16 символов для логов
                    'result_count': len(result),
                    'ttl': ttl
                })
            else:
                logger.warning(f"Не удалось закэшировать результат поиска", extra={'query_hash': query_hash[:16]})

            return bool(success)

        except Exception as e:
            logger.exception(f"Ошибка кэширования результата поиска: {e}")
            return False

    def get_cached_search_result(self, query_hash: str) -> Optional[List[Dict[str, Any]]]:
        """
        Получение закэшированного результата поиска.

        Args:
            query_hash: Хэш запроса

        Returns:
            Optional[List]: Закэшированный результат
        """
        try:
            key = f"search:{query_hash}"
            data = self._redis.get(key)

            if data:
                cached_data = json.loads(data)

                # Обновляем TTL при чтении
                remaining_ttl = self._redis.ttl(key)
                if remaining_ttl > 0:
                    new_ttl = min(600, remaining_ttl + 60)  # Добавляем 1 минуту, но не более 10 минут
                    self._redis.expire(key, new_ttl)

                logger.debug(f"Кэш попадание для запроса", extra={
                    'query_hash': query_hash[:16],
                    'result_count': cached_data.get('result_count', 0)
                })

                return cached_data.get("result", [])
            return None

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON для кэша поиска {query_hash[:16]}: {e}")
            return None
        except Exception as e:
            logger.exception(f"Ошибка получения кэшированного результата: {e}")
            return None


    def delete_task(self, task_id: str) -> bool:
        """
        Удаление задачи из кэша.

        Args:
            task_id: Идентификатор задачи

        Returns:
            bool: Успешность операции
        """
        try:
            # Удаляем все связанные ключи
            keys = [
                f"task:{task_id}",
                f"excel:{task_id}"
            ]

            deleted_count = self._redis.delete(*keys)
            logger.info(f"Задача удалена из кэша", extra={
                'task_id': task_id,
                'deleted_keys': deleted_count
            })

            return deleted_count > 0

        except Exception as e:
            logger.exception(f"Ошибка удаления задачи {task_id} из кэша: {e}")
            return False

    def cleanup_old_tasks(self, pattern: str = "task:*", batch_size: int = 100) -> int:
        """
        Очистка старых задач.

        Args:
            pattern: Паттерн для поиска ключей
            batch_size: Размер батча для удаления

        Returns:
            int: Количество удаленных ключей
        """
        try:
            deleted_count = 0
            cursor = 0

            while True:
                cursor, keys = self._redis.scan(
                    cursor=cursor,
                    match=pattern,
                    count=batch_size
                )

                if keys:
                    # Удаляем только истекшие ключи
                    pipeline = self._redis.pipeline()
                    for key in keys:
                        pipeline.ttl(key)

                    ttls = pipeline.execute()

                    expired_keys = [key for key, ttl in zip(keys, ttls) if ttl == -2 or ttl == -1]

                    if expired_keys:
                        deleted = self._redis.delete(*expired_keys)
                        deleted_count += deleted

                if cursor == 0:
                    break

            if deleted_count > 0:
                logger.info(f"Очищено старых задач: {deleted_count}")

            return deleted_count

        except Exception as e:
            logger.exception(f"Ошибка очистки старых задач: {e}")
            return 0

    def health_check(self) -> Dict[str, Any]:
        """
        Проверка здоровья Redis соединения.

        Returns:
            Dict: Статус здоровья
        """
        try:
            # Проверка ping
            ping_result = self._redis.ping()

            # Проверка доступности памяти
            info = self._redis.info()

            return {
                "status": "healthy" if ping_result else "unhealthy",
                "ping": ping_result,
                "used_memory": info.get('used_memory_human', 'unknown'),
                "connected_clients": info.get('connected_clients', 0),
                "total_keys": self._redis.dbsize()
            }

        except Exception as e:
            logger.error(f"Ошибка health check Redis: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def close(self):
        """Закрытие соединений Redis"""
        try:
            self.connection_pool.disconnect()
            logger.info("Соединения Redis закрыты")
        except Exception as e:
            logger.error(f"Ошибка закрытия соединений Redis: {e}")

    def __del__(self):
        """Деструктор"""
        try:
            self.close()
        except:
            pass