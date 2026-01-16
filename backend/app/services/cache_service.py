# backend/app/services/cache_service.py
import redis
import json
import os
from backend.app.config import Config

_redis_client = redis.from_url(f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/0")

CACHE_TTL_SECONDS = 3600  # 1 hour

def get_from_cache(query_hash: str):
    """Проверяет кэш по хешу запроса."""
    cached_data = _redis_client.get(f"cache:{query_hash}")
    if cached_data:
        return json.loads(cached_data)
    return None

def set_result_in_cache(query_hash: str, task_id: str, result_data: dict):
    """Сохраняет результат в кэш по хешу запроса."""
    cache_entry = {
        'task_id': task_id,
        'result': result_data
    }
    _redis_client.setex(f"cache:{query_hash}", CACHE_TTL_SECONDS, json.dumps(cache_entry))

def set_status(task_id: str, status: str, ttl=None):
    """Устанавливает статус задачи."""
    task_key = f"task:{task_id}"
    _redis_client.hset(task_key, mapping={"status": status})
    if ttl:
        _redis_client.expire(task_key, ttl)

def set_task_result(task_id: str, status: str, result: dict):
    """Устанавливает статус и результат задачи."""
    task_key = f"task:{task_id}"
    _redis_client.hset(task_key, mapping={"status": status, "result": json.dumps(result)})
    # Устанавливаем TTL на 1 час
    _redis_client.expire(task_key, CACHE_TTL_SECONDS)

def get_task_result(task_id: str):
    """Получает статус и результат задачи."""
    task_key = f"task:{task_id}"
    data = _redis_client.hgetall(task_key)
    if not data:
        return "not_found", None

    status = data[b'status'].decode('utf-8')
    result_str = data.get(b'result')
    result = json.loads(result_str.decode('utf-8')) if result_str else None
    return status, result

def set_excel_file_path(task_id: str, file_path: str):
    """Сохраняет путь к файлу Excel в кэше задачи."""
    task_key = f"task:{task_id}"
    _redis_client.hset(task_key, mapping={"excel_path": file_path})

def get_excel_file_path(task_id: str):
    """Получает путь к файлу Excel из кэша задачи."""
    task_key = f"task:{task_id}"
    path_bytes = _redis_client.hget(task_key, "excel_path")
    if path_bytes:
        return path_bytes.decode('utf-8')
    return None
