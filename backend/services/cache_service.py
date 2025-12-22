# backend/services/cache_service.py

import redis
import json
import os
from typing import Dict, Any, Optional

class CacheService:
    def __init__(self):
        self._redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=os.getenv("REDIS_PORT", 6379),
            db=0,
            decode_responses=True
        )

    def set_task_status(self, task_id: str, status: str, result: Optional[Dict] = None):
        key = f"task:{task_id}"
        value = {"status": status, "result": result}
        self._redis.setex(key, 3600, json.dumps(value))  # TTL 1 час

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        key = f"task:{task_id}"
        data = self._redis.get(key)
        return json.loads(data) if data else None

    def cache_search_result(self, query_hash: str, result: list):
        key = f"search:{query_hash}"
        self._redis.setex(key, 600, json.dumps(result))  # TTL 10 минут

    def get_cached_search_result(self, query_hash: str) -> Optional[list]:
        key = f"search:{query_hash}"
        data = self._redis.get(key)
        return json.loads(data) if data else None

    def cache_excel_path(self, task_id: str, path: str):
        key = f"excel:{task_id}"
        self._redis.setex(key, 86400, path)  # TTL 24 часа

    def get_cached_excel_path(self, task_id: str) -> Optional[str]:
        key = f"excel:{task_id}"
        return self._redis.get(key)