"""History handler – Max Youtube Downloader"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.repositories import DownloadRepository
from database.connection import AsyncSessionLocal

router = Router()


@router.message(Command("history"))
async def show_history(message: Message, **kwargs):
    """نمایش تاریخچه دانلودها"""
    async with AsyncSessionLocal() as session:
        download_repo = DownloadRepository(session)
        downloads = await download_repo.get_user_downloads(
            message.from_user.id, limit=10
        )

        if not downloads:
            await message.reply("📜 هنوز دانلودی نداشته‌اید.")
            return

        history_text = "📜 <b>دانلودهای اخیر شما:</b>\n\n"
        for dl in downloads:
            title = dl.title or "نامشخص"
            if len(title) > 30:
                title = title[:27] + "..."
            
            # Translate status
            status_fa = dl.status
            if dl.status == "completed":
                status_fa = "✅ موفق"
            elif dl.status == "failed":
                status_fa = "❌ ناموفق"
            elif dl.status == "downloading":
                status_fa = "⏳ در حال دانلود"

            date_str = dl.created_at.strftime("%Y-%m-%d %H:%M") if dl.created_at else "—"
            
            history_text += f"▪️ <b>{title}</b>\n"
            history_text += f"   وضعیت: {status_fa}\n"
            history_text += f"   تاریخ: <code>{date_str}</code>\n\n"

        await message.reply(history_text, parse_mode="HTML")


__all__ = ["router", "show_history"]
