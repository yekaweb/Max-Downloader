"""Authentication middleware - User registration"""
from aiogram import BaseMiddleware
from aiogram.types import Update, Message
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import AsyncSessionLocal
from database.repositories import UserRepository
from typing import Any, Callable, Dict, Awaitable


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        message = event.message
        
        if not message or not message.from_user:
            return await handler(event, data)

        # Get or create user
        async with AsyncSessionLocal() as session:
            user_repo = UserRepository(session)
            user = await user_repo.get_by_telegram_id(message.from_user.id)
            
            if not user:
                user = await user_repo.create(
                    telegram_id=message.from_user.id,
                    telegram_username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                )
            
            data["user"] = user
            data["db"] = session
            return await handler(event, data)


__all__ = ["AuthMiddleware"]
