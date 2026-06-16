"""Profile handler – Max Youtube Downloader"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.repositories import UserRepository
from database.connection import AsyncSessionLocal

router = Router()


@router.message(Command("profile"))
async def show_profile(message: Message, **kwargs):
    """نمایش پروفایل کاربر"""
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)

        if not user:
            await message.reply("❌ کاربر یافت نشد. لطفاً /start را بزنید.")
            return

        lang_emoji = "🇮🇷" if (user.language or "").startswith("fa") else "🌐"
        joined = user.created_at.strftime("%Y-%m-%d") if user.created_at else "—"

        profile_text = (
            "👤 <b>پروفایل من</b>\n\n"
            f"📝 <b>نام:</b> {user.first_name or ''} {user.last_name or ''}\n"
            f"🆔 <b>آیدی تلگرام:</b> <code>{user.telegram_id}</code>\n"
            f"{lang_emoji} <b>زبان:</b> {user.language or 'fa'}\n"
            f"📥 <b>تعداد دانلودها:</b> {user.total_downloads or 0}\n"
            f"💰 <b>سکه‌های من:</b> {int(user.total_coins or 0)}\n"
            f"📅 <b>تاریخ عضویت:</b> {joined}\n\n"
            f"🎁 <b>کد معرفی:</b> <code>{user.referral_code or 'تولید نشده'}</code>\n"
            f"👥 <b>تعداد معرفی‌ها:</b> {user.referral_count or 0}"
        )
        await message.reply(profile_text, parse_mode="HTML")


__all__ = ["router", "show_profile"]
