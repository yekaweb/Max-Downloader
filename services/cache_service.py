"""Redis cache service (async)"""
import aioredis
from config_simple import settings

_redis = None


async def get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def cache_set(key: str, value, ttl: int = None):
    r = await get_redis()
    await r.set(key, value, ex=ttl or 3600)


async def cache_get(key: str):
    r = await get_redis()
    return await r.get(key)


__all__ = ["get_redis", "cache_set", "cache_get"]
