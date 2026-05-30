"""Minimal bot loader for testing"""

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from config_simple import settings

# Initialize bot
try:
    if settings.BOT_TOKEN:
        bot = Bot(token=settings.BOT_TOKEN)
    else:
        raise ValueError("BOT_TOKEN not configured")
except Exception as e:
    print(f"⚠️  Bot initialization failed: {e}")
    bot = None

# Initialize dispatcher with memory storage
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Simple /start handler
@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command"""
    await message.reply(
        "🤖 سلام! من ربات دانلود یوتیوب هستم\n\n"
        "من می‌تونم ویدیو دانلود کنم از:\n"
        "• یوتیوب\n"
        "• اینستاگرام\n"
        "• توییتر\n\n"
        "برای شروع: /help"
    )

# Simple /help handler
@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    await message.reply(
        "📖 **دستورات موجود:**\n\n"
        "/start - شروع\n"
        "/help - کمک\n"
        "/about - درباره ما\n"
    )

# Simple /about handler
@dp.message(Command("about"))
async def cmd_about(message: Message):
    """Handle /about command"""
    await message.reply(
        "ℹ️ **درباره ربات:**\n\n"
        "DLBot v1.0.0\n"
        "ربات حرفه‌ای دانلود فایل‌ها\n"
    )

# Fallback handler
@dp.message()
async def handle_message(message: Message):
    """Handle all other messages"""
    await message.reply(
        "❌ دستور شناخته شده نیست\n"
        "برای کمک: /help"
    )

__all__ = ["bot", "dp"]
