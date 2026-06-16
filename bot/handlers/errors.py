"""Error handler – fallback for unhandled messages (Max Youtube Downloader)"""
from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def handle_unknown(message: Message, **kwargs):
    """Fallback handler: catches any message not matched by other routers"""
    text = (message.text or "").strip()

    if text.startswith("http"):
        # User sent a URL but it wasn't caught by download handler (session issue?)
        await message.reply(
            "⏳ لینک شما دریافت شد.\n"
            "در حال پردازش... اگر پاسخی نگرفتید لینک را دوباره ارسال کنید."
        )
    else:
        await message.reply(
            "❓ دستور شناخته نشد.\n\n"
            "📌 برای دریافت لیست دستورات: /help\n"
            "📥 برای دانلود، لینک ویدیو را مستقیماً ارسال کنید."
        )


__all__ = ["router"]
