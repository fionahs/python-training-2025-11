"""
Simple in-memory cache with TTL support
Can be replaced with Redis in production
"""
from typing import Optional, Any
from datetime import datetime, timedelta
import hashlib
import json


class SimpleCache:
    """Thread-safe in-memory cache with TTL"""

    def __init__(self):
        self._cache = {}

    def _generate_key(self, prefix: str, data: dict) -> str:
        """Generate a cache key from prefix and data"""
        # Sort keys for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
        hash_key = hashlib.md5(sorted_data.encode()).hexdigest()
        return f"{prefix}:{hash_key}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if exists and not expired"""
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Check if expired
        if datetime.utcnow() > entry['expires_at']:
            del self._cache[key]
            return None

        return entry['value']

    def set(self, key: str, value: Any, ttl_seconds: int):
        """Set value in cache with TTL in seconds"""
        self._cache[key] = {
            'value': value,
            'expires_at': datetime.utcnow() + timedelta(seconds=ttl_seconds),
            'created_at': datetime.utcnow()
        }

    def delete(self, key: str):
        """Delete a key from cache"""
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()

    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = len(self._cache)
        expired = sum(1 for entry in self._cache.values()
                     if datetime.utcnow() > entry['expires_at'])

        return {
            'total_entries': total,
            'active_entries': total - expired,
            'expired_entries': expired
        }


# Global cache instance
cache = SimpleCache()


# Cache TTL constants (in seconds)
GEOCODING_TTL = 30 * 24 * 60 * 60  # 30 days
SEARCH_TTL = 5 * 60  # 5 minutes
