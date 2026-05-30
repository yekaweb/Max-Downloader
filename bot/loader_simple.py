"""Bot loader with all handlers"""

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from config_simple import settings
from locales import i18n
from bot.keyboards.inline import main_menu_kb, language_kb

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

# Import handlers
try:
    from bot.handlers.download_handler import router as download_router
    dp.include_router(download_router)
except ImportError as e:
    print(f"⚠️  Failed to load download handler: {e}")


# ============ START HANDLER ============
@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command"""
    user_name = message.from_user.first_name or "دوست"
    text = i18n.get("start.title")
    desc = i18n.get("start.description")
    
    await message.answer(
        f"{text}\n\n{desc}",
        reply_markup=main_menu_kb()
    )


# ============ HELP HANDLER ============
@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    commands = i18n.get("help.commands")
    title = i18n.get("help.title")
    
    await message.answer(
        f"{title}\n\n{commands}"
    )


# ============ ABOUT HANDLER ============
@dp.message(Command("about"))
async def cmd_about(message: Message):
    """Handle /about command"""
    title = i18n.get("about.title")
    desc = i18n.get("about.description")
    features = i18n.get("about.features")
    
    await message.answer(
        f"{title}\n\n{desc}\n\n{features}"
    )


# ============ PROFILE HANDLER ============
@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    """Handle /profile command"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Unknown"
    
    profile_text = (
        f"👤 **پروفایل شما**\n\n"
        f"نام: {first_name}\n"
        f"آیدی: {user_id}\n"
        f"دانلودها: 0\n"
        f"عضویت: امروز\n"
        f"زبان: فارسی\n"
    )
    
    await message.answer(profile_text)


# ============ CALLBACK HANDLERS ============
@dp.callback_query(F.data == "download_menu")
async def handle_download_callback(callback: CallbackQuery):
    """Handle download menu callback"""
    await callback.answer()


@dp.callback_query(F.data == "profile")
async def handle_profile_callback(callback: CallbackQuery):
    """Show profile from callback"""
    user_id = callback.from_user.id
    first_name = callback.from_user.first_name or "Unknown"
    
    profile_text = (
        f"👤 **پروفایل شما**\n\n"
        f"نام: {first_name}\n"
        f"آیدی: {user_id}\n"
        f"دانلودها: 0\n"
        f"زبان: فارسی\n"
    )
    
    await callback.message.edit_text(profile_text)
    await callback.answer()


@dp.callback_query(F.data == "settings")
async def handle_settings(callback: CallbackQuery):
    """Settings menu"""
    settings_text = (
        "⚙️ **تنظیمات**\n\n"
        "🌐 زبان: فارسی\n"
        "🔔 اطلاع‌رسانی: فعال\n"
        "🔒 حریم خصوصی: محفوظ\n"
    )
    
    await callback.message.edit_text(settings_text)
    await callback.answer()


@dp.callback_query(F.data == "guide")
async def handle_guide(callback: CallbackQuery):
    """User guide"""
    guide = i18n.get("guide.user_guide")
    
    await callback.message.edit_text(guide)
    await callback.answer()


@dp.callback_query(F.data == "about_menu")
async def handle_about_menu(callback: CallbackQuery):
    """About from menu"""
    title = i18n.get("about.title")
    desc = i18n.get("about.description")
    
    text = f"{title}\n\n{desc}"
    
    await callback.message.edit_text(text)
    await callback.answer()


@dp.callback_query(F.data == "lang_fa")
async def set_lang_fa(callback: CallbackQuery):
    """Set Persian language"""
    await callback.answer("✅ زبان تعیین شد: فارسی", show_alert=False)


@dp.callback_query(F.data == "lang_en")
async def set_lang_en(callback: CallbackQuery):
    """Set English language"""
    await callback.answer("✅ Language set to: English", show_alert=False)


# ============ FALLBACK HANDLER ============
@dp.message()
async def handle_message(message: Message):
    """Handle all other messages"""
    await message.reply(
        "❌ دستور شناخته شده نیست\n"
        "برای دانلود: /download\n"
        "برای راهنما: /help"
    )


__all__ = ["bot", "dp"]
