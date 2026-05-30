"""Main download handler for YouTube, Instagram, Twitter"""

import re
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from config_simple import settings
from locales import i18n
from bot.keyboards.inline import (
    main_menu_kb,
    download_platform_kb,
    admin_menu_kb,
    language_kb
)

router = Router()

# State tracking
user_state = {}  # Simple state for demo


@router.message(Command("download"))
async def cmd_download(message: Message):
    """دستور دانلود - انتخاب پلتفرم"""
    text = i18n.get("download.title", message.from_user.id % 2 and "en" or "fa")
    desc = i18n.get("download.description")
    
    await message.answer(
        f"{text}\n\n{desc}",
        reply_markup=download_platform_kb()
    )


@router.callback_query(F.data == "download_menu")
async def download_menu(callback: CallbackQuery):
    """منوی دانلود"""
    desc = i18n.get("download.description")
    
    await callback.message.edit_text(
        f"📥 **دانلود ویدیو**\n\n{desc}",
        reply_markup=download_platform_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "platform_youtube")
async def handle_youtube(callback: CallbackQuery):
    """YouTube platform selected"""
    await callback.message.edit_text(
        "🎥 YouTube\n\n"
        "لطفا لینک ویدیو YouTube را ارسال کنید:\n\n"
        "مثال: https://youtu.be/... یا https://youtube.com/watch?v=..."
    )
    user_state[callback.from_user.id] = "waiting_youtube_url"
    await callback.answer()


@router.callback_query(F.data == "platform_instagram")
async def handle_instagram(callback: CallbackQuery):
    """Instagram platform selected"""
    await callback.message.edit_text(
        "📸 Instagram\n\n"
        "لطفا لینک پست یا ویدیو Instagram را ارسال کنید:\n\n"
        "مثال: https://instagram.com/p/... یا https://instagram.com/reel/..."
    )
    user_state[callback.from_user.id] = "waiting_instagram_url"
    await callback.answer()


@router.callback_query(F.data == "platform_twitter")
async def handle_twitter(callback: CallbackQuery):
    """Twitter platform selected"""
    await callback.message.edit_text(
        "🐦 Twitter (X)\n\n"
        "لطفا لینک توییت را ارسال کنید:\n\n"
        "مثال: https://twitter.com/... یا https://x.com/..."
    )
    user_state[callback.from_user.id] = "waiting_twitter_url"
    await callback.answer()


@router.message(F.text.contains("youtu"))
async def handle_youtube_url(message: Message):
    """دریافت لینک YouTube"""
    url = message.text.strip()
    
    # Validate YouTube URL
    if not re.search(r"(youtube\.com|youtu\.be)", url):
        await message.reply("❌ لینک YouTube نامعتبر است!")
        return
    
    # Show processing
    status_msg = await message.answer("⏳ درحال دانلود ویدیو...")
    
    try:
        # Simulate download (in real: use yt-dlp)
        await asyncio.sleep(2)
        
        await status_msg.edit_text("📤 درحال آپلود...")
        await asyncio.sleep(1)
        
        # Send dummy response
        await message.answer(
            "✅ ویدیو دانلود شد!\n\n"
            "📹 عنوان: Sample Video\n"
            "⏱️ مدت: 5:30\n"
            "📊 کیفیت: 1080p\n\n"
            "فایل ویدیو به شما ارسال می‌شود..."
        )
        
        # Send file (dummy)
        await message.answer("📁 فایل نمونه")
        
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(f"❌ خطا: {str(e)}")


@router.message(F.text.contains("instagram"))
async def handle_instagram_url(message: Message):
    """دریافت لینک Instagram"""
    url = message.text.strip()
    
    if not re.search(r"instagram\.com", url):
        await message.reply("❌ لینک Instagram نامعتبر است!")
        return
    
    status_msg = await message.answer("⏳ درحال دانلود...")
    
    try:
        await asyncio.sleep(2)
        await status_msg.edit_text("📤 درحال آپلود...")
        await asyncio.sleep(1)
        
        await message.answer("✅ محتوای Instagram دانلود شد!")
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(f"❌ خطا: {str(e)}")


@router.message(F.text.contains("twitter") | F.text.contains("x.com"))
async def handle_twitter_url(message: Message):
    """دریافت لینک Twitter"""
    url = message.text.strip()
    
    if not re.search(r"(twitter\.com|x\.com)", url):
        await message.reply("❌ لینک Twitter نامعتبر است!")
        return
    
    status_msg = await message.answer("⏳ درحال دانلود...")
    
    try:
        await asyncio.sleep(2)
        await status_msg.edit_text("📤 درحال آپلود...")
        await asyncio.sleep(1)
        
        await message.answer("✅ محتوای Twitter دانلود شد!")
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(f"❌ خطا: {str(e)}")


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """آمار ادمین"""
    user_id = callback.from_user.id
    admin_ids = [int(x.strip()) for x in settings.ADMIN_IDS.split(",") if x.strip()]
    
    if user_id not in admin_ids:
        await callback.answer("❌ شما مدیر نیستید!", show_alert=True)
        return
    
    stats_text = (
        "📊 **آمار سیستم:**\n\n"
        "👥 کل کاربران: 42\n"
        "🟢 کاربران فعال: 15\n"
        "📥 کل دانلودها: 187\n"
        "📅 دانلودهای امروز: 23\n"
    )
    
    await callback.message.edit_text(stats_text)
    await callback.answer()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    """پنل ادمین"""
    user_id = message.from_user.id
    admin_ids = [int(x.strip()) for x in settings.ADMIN_IDS.split(",") if x.strip()]
    
    if user_id not in admin_ids:
        await message.answer("❌ شما مدیر نیستید!")
        return
    
    admin_text = (
        "⚙️ **پنل مدیریت**\n\n"
        "سلام مدیر! شما می‌توانید:\n"
        "• مشاهده آمار\n"
        "• ارسال پیام عمومی\n"
        "• مدیریت کاربران"
    )
    
    await message.answer(admin_text, reply_markup=admin_menu_kb())


@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    """بازگشت به منوی اصلی"""
    text = i18n.get("start.title")
    desc = i18n.get("start.description")
    
    await callback.message.edit_text(
        f"{text}\n\n{desc}",
        reply_markup=main_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "download_menu")
async def download_menu(callback: CallbackQuery):
    """منوی دانلود"""
    desc = i18n.get("download.description")
    
    await callback.message.edit_text(
        f"📥 **دانلود ویدیو**\n\n{desc}",
        reply_markup=download_platform_kb()
    )
    await callback.answer()


__all__ = ["router"]
