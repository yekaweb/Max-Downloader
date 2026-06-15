"""Rate limiting middleware"""
from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Any, Callable, Dict, Awaitable
from services.cache_service import cache_get, cache_set


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, calls: int = 20, period: int = 60):
        self.calls = calls
        self.period = period

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        
        # Only rate limit messages and callbacks
        user_id = None
        if event.message and event.message.from_user:
            user_id = event.message.from_user.id
            reply_func = event.message.reply
        elif event.callback_query and event.callback_query.from_user:
            user_id = event.callback_query.from_user.id
            reply_func = event.callback_query.answer
        
        if not user_id:
            return await handler(event, data)
        
        key = f"rate_limit:{user_id}"
        
        count = await cache_get(key)
        count = int(count) if count else 0
        
        if count >= self.calls:
            # Rate limited
            try:
                await reply_func("⏱ شما بیش از حد مجاز درخواست داده‌اید. لطفاً کمی صبر کنید.")
            except:
                pass
            return  # Ignore the update
        
        await cache_set(key, count + 1, ttl=self.period)
        return await handler(event, data)


__all__ = ["RateLimitMiddleware"]
