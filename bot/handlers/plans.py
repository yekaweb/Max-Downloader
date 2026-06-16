"""Plans handler – Max Youtube Downloader"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


@router.message(Command("plans"))
async def show_plans(message: Message, **kwargs):
    """نمایش پلن‌های اشتراک"""
    plans_text = (
        "💳 <b>پلن‌های اشتراک</b>\n\n"
        "🆓 <b>رایگان (Free)</b>\n"
        "🔹 محدودیت دانلود: ۵ در روز\n"
        "🔹 حداکثر کیفیت: 720p\n"
        "🔹 هزینه: رایگان\n\n"
        "⭐ <b>ویژه (Premium)</b>\n"
        "🔸 محدودیت دانلود: نامحدود\n"
        "🔸 حداکثر کیفیت: 1080p\n"
        "🔸 هزینه: ۵۰ هزار تومان / ماه\n\n"
        "🚀 <b>وی‌آی‌پی (VIP)</b>\n"
        "💎 محدودیت دانلود: نامحدود\n"
        "💎 حداکثر کیفیت: 4K\n"
        "💎 پشتیبانی: اولویت بالا\n"
        "💎 هزینه: ۱۵۰ هزار تومان / ماه"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ خرید اشتراک ویژه", callback_data="plan_premium")],
            [InlineKeyboardButton(text="🚀 خرید اشتراک VIP", callback_data="plan_vip")],
        ]
    )

    await message.reply(plans_text, reply_markup=keyboard, parse_mode="HTML")


__all__ = ["router", "show_plans"]
