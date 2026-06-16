"""Help handler – Max Youtube Downloader"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

BOT_NAME = "Max Youtube Downloader"


@router.message(Command("help"))
async def show_help(message: Message, **kwargs):
    """نمایش راهنمای ربات"""
    help_text = (
        f"❓ <b>راهنمای {BOT_NAME}</b>\n\n"
        "<b>📌 دستورات کاربر:</b>\n"
        "/start — شروع کار با ربات\n"
        "/help — نمایش این راهنما\n"
        "/profile — مشاهده پروفایل من\n"
        "/history — تاریخچه دانلودها\n"
        "/plans — مشاهده پلن‌های اشتراک\n"
        "/referral — برنامه معرفی و سکه\n\n"
        "<b>🛠 دستورات مدیر:</b>\n"
        "/admin — ورود به پنل مدیریت\n\n"
        "<b>📥 نحوه استفاده:</b>\n"
        "۱. لینک ویدیو یا موزیک خود را بفرستید\n"
        "   (یوتیوب، اینستاگرام، تیک‌تاک، توییتر و...)\n"
        "۲. کیفیت دلخواه را انتخاب کنید\n"
        "۳. فایل برای شما ارسال می‌شود!\n\n"
        f"🚀 از {BOT_NAME} لذت ببرید!"
    )
    await message.reply(help_text, parse_mode="HTML")


__all__ = ["router", "show_help"]
