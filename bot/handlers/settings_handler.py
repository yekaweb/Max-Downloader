"""Settings handler – Max Youtube Downloader"""
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.connection import AsyncSessionLocal
from database.repositories import UserRepository

router = Router()

def get_settings_keyboard(language="fa", default_quality="720p"):
    """ایجاد کیبورد تنظیمات"""
    lang_btn = "🇮🇷 فارسی" if language == "fa" else "🇬🇧 English"
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🌐 زبان (Language)", callback_data="ignore"),
                InlineKeyboardButton(text=lang_btn, callback_data="toggle_lang")
            ],
            [
                InlineKeyboardButton(text="📺 کیفیت پیش‌فرض", callback_data="ignore"),
                InlineKeyboardButton(text=f"⚙️ {default_quality}", callback_data="toggle_quality")
            ],
            [InlineKeyboardButton(text="❌ بستن", callback_data="close_settings")]
        ]
    )

@router.callback_query(F.data == "ignore")
async def ignore_callback(query: CallbackQuery):
    try:
        await query.answer()
    except Exception:
        pass

@router.callback_query(F.data == "close_settings")
async def close_settings(query: CallbackQuery):
    await query.message.delete()
    try:
        await query.answer()
    except Exception:
        pass

from aiogram.exceptions import TelegramBadRequest

@router.callback_query(F.data == "toggle_lang")
async def toggle_language(query: CallbackQuery):
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(query.from_user.id)
        if not user:
            await query.answer("❌ کاربر یافت نشد")
            return
            
        new_lang = "en" if user.language == "fa" else "fa"
        await user_repo.update(user.id, language=new_lang)
        
        # در اینجا کیفیت پیش‌فرض را از دیتابیس می‌خوانیم، اما فعلا یک فیلد نداریم.
        # پس فقط زبان را ذخیره می‌کنیم
        
        try:
            await query.message.edit_reply_markup(
                reply_markup=get_settings_keyboard(language=new_lang)
            )
        except TelegramBadRequest:
            pass
            
        msg = "✅ زبان به انگلیسی تغییر یافت" if new_lang == "en" else "✅ زبان به فارسی تغییر یافت"
        await query.answer(msg)

@router.callback_query(F.data == "toggle_quality")
async def toggle_quality(query: CallbackQuery):
    # از آنجایی که فیلد کیفیت پیش فرض در مدل کاربر وجود ندارد، 
    # به صورت نمایشی کیفیت را بین مقادیر پرکاربرد جابه‌جا می‌کنیم (میتوانید در آینده به دیتابیس اضافه کنید)
    current_markup = query.message.reply_markup
    current_quality = "720p"
    
    # پیدا کردن کیفیت فعلی از روی دکمه
    for row in current_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data == "toggle_quality":
                current_quality = btn.text.replace("⚙️ ", "")
                break
                
    qualities = ["360p", "480p", "720p", "1080p", "4K", "Audio (MP3)"]
    try:
        idx = qualities.index(current_quality)
        new_quality = qualities[(idx + 1) % len(qualities)]
    except ValueError:
        new_quality = "720p"
        
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(query.from_user.id)
        lang = user.language if user else "fa"
        
    try:
        await query.message.edit_reply_markup(
            reply_markup=get_settings_keyboard(language=lang, default_quality=new_quality)
        )
    except TelegramBadRequest:
        pass
        
    await query.answer(f"✅ کیفیت پیش‌فرض به {new_quality} تغییر کرد")

async def show_settings_panel(message: Message):
    """تابع اصلی نمایش تنظیمات"""
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        
        if not user:
            await message.reply("❌ کاربر یافت نشد. لطفاً /start را بزنید.")
            return
            
        lang = user.language or "fa"
        
        settings_text = (
            "⚙️ **تنظیمات ربات**\n\n"
            "از طریق دکمه‌های زیر می‌توانید تنظیمات حساب خود را شخصی‌سازی کنید."
        )
        
        await message.reply(
            settings_text, 
            reply_markup=get_settings_keyboard(language=lang),
            parse_mode="Markdown"
        )

__all__ = ["router", "show_settings_panel"]
