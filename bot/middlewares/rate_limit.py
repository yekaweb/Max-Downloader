"""Rate limiting middleware"""
from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Any, Callable, Dict, Awaitable
from services.cache_service import cache_get, cache_set


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, calls: int = 30, period: int = 60):
        self.calls = calls
        self.period = period

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        message = event.message
        
        if not message or not message.from_user:
            return await handler(event, data)
        
        user_id = message.from_user.id
        key = f"rate_limit:{user_id}"
        
        count = await cache_get(key)
        count = int(count) if count else 0
        
        if count >= self.calls:
            # Rate limited
            return  # Silently ignore
        
        await cache_set(key, count + 1, ttl=self.period)
        return await handler(event, data)


__all__ = ["RateLimitMiddleware"]
