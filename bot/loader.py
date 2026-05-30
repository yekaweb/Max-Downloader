"""Bot Loader - Initialize aiogram bot and dispatcher"""

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config_simple import settings
from bot.handlers import routers

# Initialize bot (token expected in environment/.env)
try:
    if settings.BOT_TOKEN:
        bot = Bot(token=settings.BOT_TOKEN)
    else:
        raise ValueError("BOT_TOKEN not configured")
except Exception as e:
    # Lazy placeholder for environments where token is not set yet
    print(f"⚠️  Bot initialization warning: {e}")
    bot = None

# Initialize dispatcher with memory storage
storage = MemoryStorage()
try:
    dp = Dispatcher(storage=storage)
    # Include all routers
    for router in routers:
        dp.include_router(router)
except Exception as e:
    print(f"⚠️  Dispatcher initialization warning: {e}")
    dp = None

__all__ = ["bot", "dp"]
