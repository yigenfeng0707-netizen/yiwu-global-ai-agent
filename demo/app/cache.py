"""义乌小商品出海智能体 - TTL缓存层"""

import time
import hashlib
import json
from typing import Any, Optional, Callable, Dict
from functools import wraps


class TTLCache:
    """带TTL的内存缓存 - 用于数据源查询结果缓存"""

    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值，过期返回None"""
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None
        if time.time() > entry["expires_at"]:
            del self._cache[key]
            self._misses += 1
            return None
        self._hits += 1
        return entry["value"]

    def set(self, key: str, value: Any, ttl: int = 0):
        """设置缓存值"""
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + (ttl or self._default_ttl),
            "created_at": time.time(),
        }

    def invalidate(self, key: str):
        """使缓存失效"""
        self._cache.pop(key, None)

    def clear(self):
        """清空所有缓存"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def cleanup_expired(self):
        """清理过期条目"""
        now = time.time()
        expired = [k for k, v in self._cache.items() if now > v["expires_at"]]
        for k in expired:
            del self._cache[k]

    @property
    def stats(self) -> Dict[str, Any]:
        """缓存统计"""
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{self._hits / total * 100:.1f}%" if total > 0 else "0%",
        }


def make_cache_key(*args, **kwargs) -> str:
    """生成缓存键"""
    parts = [str(a) for a in args]
    parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    raw = "|".join(parts)
    return hashlib.md5(raw.encode()).hexdigest()


# 全局缓存实例
cache = TTLCache(default_ttl=300)


def cached(ttl: int = 300):
    """缓存装饰器 - 用于Agent方法缓存"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__module__}.{func.__qualname__}:{make_cache_key(*args, **kwargs)}"
            result = cache.get(key)
            if result is not None:
                return result
            result = await func(*args, **kwargs)
            cache.set(key, result, ttl=ttl)
            return result
        return wrapper
    return decorator
