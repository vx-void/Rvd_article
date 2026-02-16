"""Search result caching."""

import hashlib
import json
from typing import Optional

from cachetools import TTLCache

from backend.app.models.search import SearchResponse


class SearchCache:
    """In-memory cache for search results."""

    def __init__(self, maxsize: int = 1000, ttl: int = 300):
        self._cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)

    def _make_key(self, query: str, top_k: int, filters: Optional[dict]) -> str:
        """Generate cache key."""
        key_data = {
            "query": query.lower().strip(),
            "top_k": top_k,
            "filters": filters,
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()[:32]

    def get(self, query: str, top_k: int, filters: Optional[dict]) -> Optional[SearchResponse]:
        """Get cached result."""
        key = self._make_key(query, top_k, filters)
        return self._cache.get(key)

    def set(
            self,
            query: str,
            top_k: int,
            filters: Optional[dict],
            response: SearchResponse,
    ) -> None:
        """Cache result."""
        key = self._make_key(query, top_k, filters)
        self._cache[key] = response

    def clear(self) -> None:
        """Clear all cached results."""
        self._cache.clear()

    def stats(self) -> dict:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "maxsize": self._cache.maxsize,
            "currsize": self._cache.currsize,
        }