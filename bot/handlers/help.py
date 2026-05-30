"""Help handler"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help"))
async def show_help(message: Message):
    """Show help message"""
    help_text = """
❓ **Available Commands**

**User Commands:**
/start - Start the bot
/help - Show this help message
/profile - View your profile
/history - Download history
/plans - View subscription plans
/referral - Referral information

**Admin Commands:**
/admin - Admin dashboard
/stats - Bot statistics

📝 **How to use:**
1. Send a link (YouTube, Instagram, etc.)
2. Select quality
3. Download will start!

🚀 Enjoy DLBot!
"""
    await message.reply(help_text, parse_mode="Markdown")


__all__ = ["router"]
