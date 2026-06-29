from typing import Any, Optional
import json


class AICache:
    """
    Caching engine for expensive AI generations.
    In a real implementation, this would connect to Redis and invalidate
    based on Digital Twin timestamp updates.
    """

    def __init__(self):
        self._cache = {}  # Mock in-memory cache for now

    async def get(self, key: str) -> Optional[str]:
        return self._cache.get(key)

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        self._cache[key] = value

    async def invalidate_for_member(self, member_id: str) -> None:
        """
        Invalidates all cached AI generations for a specific member.
        Called when their Digital Twin changes.
        """
        keys_to_delete = [k for k in self._cache.keys() if member_id in k]
        for k in keys_to_delete:
            del self._cache[k]
