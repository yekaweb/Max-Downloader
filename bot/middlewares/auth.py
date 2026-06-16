"""Authentication middleware - User registration (Max Youtube Downloader)"""
import logging
from aiogram import BaseMiddleware
from aiogram.types import Update
from database.connection import AsyncSessionLocal
from database.repositories import UserRepository
from typing import Any, Callable, Dict, Awaitable

logger = logging.getLogger(__name__)


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

        # Create session manually so it stays alive for the entire handler chain
        # (including callbacks that may run after the handler returns)
        session = AsyncSessionLocal()
        try:
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
            data["db"] = session        # legacy name
            data["session"] = session   # alias — download.py uses "session" param

            return await handler(event, data)

        except Exception as e:
            logger.error(f"[AuthMiddleware] Error: {e}")
            raise
        finally:
            # Always close the session, even if handler raises
            await session.close()


__all__ = ["AuthMiddleware"]
