"""History handler - download history"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.repositories import DownloadRepository
from database.connection import AsyncSessionLocal

router = Router()


@router.message(Command("history"))
async def show_history(message: Message):
    """Show download history"""
    async with AsyncSessionLocal() as session:
        download_repo = DownloadRepository(session)
        downloads = await download_repo.get_user_downloads(
            message.from_user.id, limit=10
        )
        
        if not downloads:
            await message.reply("📜 No downloads yet")
            return
        
        history_text = "📜 **Your Recent Downloads**\n\n"
        for dl in downloads:
            history_text += f"• {dl.title or 'Unknown'}\n"
            history_text += f"  Status: {dl.status}\n"
            history_text += f"  Date: {dl.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        await message.reply(history_text, parse_mode="Markdown")


__all__ = ["router"]
