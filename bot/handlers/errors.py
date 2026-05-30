"""Error handler - global error handling"""
from aiogram import Router, F
from aiogram.types import Message


router = Router()


@router.message()
async def handle_errors(message: Message):
    """Fallback handler for unhandled messages"""
    await message.reply(
        "❌ Unknown command. Please use /help for available commands.",
        parse_mode="Markdown"
    )


__all__ = ["router"]
