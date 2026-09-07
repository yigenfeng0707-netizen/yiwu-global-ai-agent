"""测试缓存模块"""

import time
import pytest
from app.cache import TTLCache, make_cache_key


class TestTTLCache:
    def test_set_and_get(self):
        cache = TTLCache(default_ttl=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_missing_key(self):
        cache = TTLCache()
        assert cache.get("nonexistent") is None

    def test_ttl_expiry(self):
        cache = TTLCache(default_ttl=1)
        cache.set("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1"
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_invalidate(self):
        cache = TTLCache()
        cache.set("key1", "value1")
        cache.invalidate("key1")
        assert cache.get("key1") is None

    def test_clear(self):
        cache = TTLCache()
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.clear()
        assert cache.stats["size"] == 0

    def test_stats(self):
        cache = TTLCache()
        cache.set("k1", "v1")
        cache.get("k1")  # hit
        cache.get("k2")  # miss
        stats = cache.stats
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1

    def test_cleanup_expired(self):
        cache = TTLCache(default_ttl=1)
        cache.set("k1", "v1", ttl=1)
        cache.set("k2", "v2", ttl=60)
        time.sleep(1.1)
        cache.cleanup_expired()
        assert cache.get("k1") is None
        assert cache.get("k2") == "v2"

    def test_complex_values(self):
        cache = TTLCache()
        data = {"list": [1, 2, 3], "nested": {"a": True}}
        cache.set("complex", data)
        assert cache.get("complex") == data


class TestCacheKey:
    def test_deterministic(self):
        key1 = make_cache_key("a", "b", x=1)
        key2 = make_cache_key("a", "b", x=1)
        assert key1 == key2

    def test_different_args(self):
        key1 = make_cache_key("a")
        key2 = make_cache_key("b")
        assert key1 != key2

    def test_kwargs_order_independent(self):
        key1 = make_cache_key(x=1, y=2)
        key2 = make_cache_key(y=2, x=1)
        assert key1 == key2
