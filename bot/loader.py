"""Bot Loader - Initialize aiogram bot and dispatcher."""

from __future__ import annotations
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers import routers

from config import settings

try:
    from aiogram.fsm.storage.redis import RedisStorage
except ImportError:  # pragma: no cover
    RedisStorage = None


def _create_storage():
    if settings.REDIS_ENABLED and RedisStorage is not None:
        try:
            return RedisStorage.from_url(settings.redis_url)
        except Exception as exc:
            logging.warning(
                "⚠️ RedisStorage initialization failed, falling back to MemoryStorage: %s",
                exc,
            )
    return MemoryStorage()


def _create_bot():
    if not settings.BOT_TOKEN:
        raise ValueError("BOT_TOKEN not configured")

    return Bot(token=settings.BOT_TOKEN, session=AiohttpSession(timeout=120))


bot = None
storage = _create_storage()

try:
    bot = _create_bot()
except Exception as exc:
    logging.warning("⚠️ Bot initialization warning: %s", exc)
    bot = None

try:
    dp = Dispatcher(storage=storage)
    for router in routers:
        dp.include_router(router)
except Exception as exc:
    logging.warning("⚠️ Dispatcher initialization warning: %s", exc)
    dp = None

__all__ = ["bot", "dp", "storage"]
