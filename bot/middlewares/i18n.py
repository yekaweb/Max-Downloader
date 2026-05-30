"""i18n middleware - language support"""
from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Any, Callable, Dict, Awaitable
from database.repositories import UserRepository
from database.connection import AsyncSessionLocal


class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        message = event.message
        
        if message and message.from_user:
            async with AsyncSessionLocal() as session:
                user_repo = UserRepository(session)
                user = await user_repo.get_by_telegram_id(message.from_user.id)
                
                if user:
                    data["language"] = user.language
                else:
                    data["language"] = "fa"  # Default language
        
        return await handler(event, data)


__all__ = ["I18nMiddleware"]
