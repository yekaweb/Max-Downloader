"""Menu handler: Routes reply keyboard button clicks to their respective commands"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

# Import command handlers directly to call them
from bot.handlers.profile import show_profile
from bot.handlers.plans import show_plans
from bot.handlers.referral import show_referral
from bot.handlers.history import show_history
from bot.handlers.help import show_help
from bot.handlers.download_handler import admin_panel

router = Router()

@router.message(F.text == "👤 پروفایل من")
async def menu_profile(message: Message, db=None, **kwargs):
    # Route to profile handler
    # Note: we might need to recreate the kwargs depending on the handler signature
    if db:
        await show_profile(message, session=db)
    else:
        await show_profile(message)

@router.message(F.text == "💳 خرید اشتراک / سکه")
async def menu_plans(message: Message, db=None, **kwargs):
    if db:
        await show_plans(message, session=db)
    else:
        await show_plans(message)

@router.message(F.text == "👥 معرفی به دوستان")
async def menu_referral(message: Message, db=None, **kwargs):
    if db:
        await show_referral(message, session=db)
    else:
        await show_referral(message)

@router.message(F.text == "📊 تاریخچه دانلودها")
async def menu_history(message: Message, db=None, **kwargs):
    if db:
        await show_history(message, session=db)
    else:
        await show_history(message)

@router.message(F.text == "🆘 راهنما / پشتیبانی")
async def menu_help(message: Message, **kwargs):
    await show_help(message)

@router.message(F.text == "📥 دانلود جدید (ارسال لینک)")
async def menu_download(message: Message, **kwargs):
    await message.reply("لینک ویدیو یا آهنگ خود را (از یوتیوب، اینستاگرام، تیک‌تاک و...) ارسال کنید تا دانلود شروع شود 📥")

@router.message(F.text == "⚙️ تنظیمات")
async def menu_settings(message: Message, **kwargs):
    await message.reply("بخش تنظیمات به زودی اضافه خواهد شد ⚙️")

@router.message(F.text == "🛠 پنل مدیریت (Admin)")
async def menu_admin(message: Message, db=None, **kwargs):
    # Route to admin panel if user is admin
    from config import settings
    if message.from_user.id in settings.ADMIN_IDS:
        if db:
            await admin_panel(message, session=db)
        else:
            await admin_panel(message)
    else:
        await message.reply("شما دسترسی ادمین ندارید ❌")

__all__ = ["router"]
