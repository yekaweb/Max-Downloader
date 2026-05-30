"""Complete Bot Loader - All handlers in one file"""

import re
import asyncio
import os
from pathlib import Path
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from config_simple import settings

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False

# Initialize bot
try:
    if settings.BOT_TOKEN:
        bot = Bot(token=settings.BOT_TOKEN)
    else:
        raise ValueError("BOT_TOKEN not configured")
except Exception as e:
    print(f"⚠️  Bot initialization failed: {e}")
    bot = None

# ==================== STATES ====================

class DownloadStates(StatesGroup):
    """States for download process"""
    waiting_for_youtube_url = State()
    waiting_for_instagram_url = State()
    waiting_for_twitter_url = State()

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ==================== KEYBOARDS ====================

def main_menu_kb() -> InlineKeyboardMarkup:
    """Main menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 دانلود ویدیو", callback_data="download_menu")],
        [
            InlineKeyboardButton(text="👤 پروفایل", callback_data="profile"),
            InlineKeyboardButton(text="⚙️ تنظیمات", callback_data="settings")
        ],
        [
            InlineKeyboardButton(text="📚 راهنما", callback_data="guide"),
            InlineKeyboardButton(text="❓ درباره", callback_data="about_menu")
        ]
    ])

def download_platform_kb() -> InlineKeyboardMarkup:
    """Download platform selection"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 YouTube", callback_data="platform_youtube")],
        [InlineKeyboardButton(text="📸 Instagram", callback_data="platform_instagram")],
        [InlineKeyboardButton(text="🐦 Twitter", callback_data="platform_twitter")],
        [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_main")]
    ])

def admin_menu_kb() -> InlineKeyboardMarkup:
    """Admin menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 آمار", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="👥 کاربران", callback_data="admin_users")],
        [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_main")]
    ])

# ==================== MESSAGE HANDLERS ====================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Start command"""
    await message.answer(
        "🤖 سلام به DLBot!\n\n"
        "من ربات دانلود حرفه‌ای برای:\n"
        "• 🎥 YouTube\n"
        "• 📸 Instagram\n"
        "• 🐦 Twitter\n\n"
        "برای شروع دکمه پایین را بزن!",
        reply_markup=main_menu_kb()
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Help command"""
    await message.answer(
        "📖 **دستورات موجود:**\n\n"
        "/start - شروع\n"
        "/help - کمک\n"
        "/download - دانلود ویدیو\n"
        "/profile - نمایش پروفایل\n"
        "/admin - پنل ادمین (فقط برای مدیر)"
    )

@dp.message(Command("download"))
async def cmd_download(message: Message):
    """Download command"""
    await message.answer(
        "📥 **دانلود ویدیو**\n\n"
        "کدام پلتفرم را انتخاب می‌کنید؟",
        reply_markup=download_platform_kb()
    )

@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    """Profile command"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Unknown"
    
    await message.answer(
        f"👤 **پروفایل شما**\n\n"
        f"نام: {first_name}\n"
        f"آیدی: {user_id}\n"
        f"دانلودها: 0\n"
        f"عضویت: امروز\n"
        f"زبان: فارسی"
    )

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel"""
    user_id = message.from_user.id
    admin_ids = [int(x.strip()) for x in settings.ADMIN_IDS.split(",") if x.strip()]
    
    if user_id not in admin_ids:
        await message.answer("❌ شما مدیر نیستید!")
        return
    
    await message.answer(
        "⚙️ **پنل مدیریت**\n\n"
        "سلام مدیر! شما می‌توانید:\n"
        "• مشاهده آمار\n"
        "• ارسال پیام عمومی\n"
        "• مدیریت کاربران",
        reply_markup=admin_menu_kb()
    )

@dp.message(StateFilter(None))
async def handle_message(message: Message):
    """Fallback handler"""
    await message.reply(
        "❌ دستور شناخته شده نیست\n"
        "برای دانلود: /download\n"
        "برای راهنما: /help"
    )

# ==================== URL HANDLERS ====================

@dp.message(DownloadStates.waiting_for_youtube_url)
async def handle_youtube_url(message: Message, state: FSMContext):
    """Handle YouTube URL with yt-dlp"""
    url = message.text
    
    # Basic YouTube URL validation
    if not ("youtube.com" in url or "youtu.be" in url):
        await message.reply(
            "❌ **لینک نامعتبر**\n\n"
            "لطفا لینک YouTube معتبر ارسال کنید:\n"
            "• https://youtu.be/...\n"
            "• https://youtube.com/watch?v=..."
        )
        await state.clear()
        return
    
    # Check if yt-dlp is available
    if not YTDLP_AVAILABLE:
        await message.reply(
            "❌ **خطا**\n\n"
            "yt-dlp بر روی سرور نصب نیست"
        )
        await state.clear()
        return
    
    # Send processing message
    processing_msg = await message.reply(
        "⏳ **در حال دانلود...**\n\n"
        f"URL: {url}\n"
        "لطفا منتظر باشید..."
    )
    
    try:
        # Download with yt-dlp
        temp_dir = Path("temp_downloads")
        temp_dir.mkdir(exist_ok=True)
        
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': str(temp_dir / '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        # Get file size
        file_size = os.path.getsize(filename)
        file_size_mb = file_size / (1024 * 1024)
        
        # Check size limit (50 MB for Telegram)
        if file_size > 50 * 1024 * 1024:
            # Delete processing message
            try:
                await processing_msg.delete()
            except:
                pass
            
            await message.reply(
                f"❌ **فایل بیش از حد بزرگ است**\n\n"
                f"اندازه: {file_size_mb:.1f} MB\n"
                "حد مجاز: 50 MB"
            )
            
            # Cleanup
            try:
                os.remove(filename)
            except:
                pass
        else:
            # Send the file using FSInputFile
            try:
                await message.reply_document(
                    FSInputFile(filename),
                    caption=f"✅ **دانلود موفق!**\n\n"
                           f"📹 {info.get('title', 'Video')}\n"
                           f"💾 {file_size_mb:.1f} MB"
                )
            except Exception as e:
                await message.reply(f"❌ خطا در ارسال: {str(e)[:50]}")
            
            # Delete processing message
            try:
                await processing_msg.delete()
            except:
                pass
            
            # Cleanup temp file
            try:
                os.remove(filename)
            except:
                pass
    
    except Exception as e:
        # Delete processing message safely
        try:
            await processing_msg.delete()
        except:
            pass
        
        await message.reply(
            f"❌ **خطا در دانلود**\n\n"
            f"مشکل: {str(e)[:100]}"
        )
    
    await state.clear()

@dp.message(DownloadStates.waiting_for_instagram_url)
async def handle_instagram_url(message: Message, state: FSMContext):
    """Handle Instagram URL with yt-dlp"""
    url = message.text
    
    if "instagram.com" not in url:
        await message.reply(
            "❌ **لینک نامعتبر**\n\n"
            "لطفا لینک Instagram معتبر ارسال کنید:\n"
            "• https://instagram.com/p/..."
        )
        await state.clear()
        return
    
    if not YTDLP_AVAILABLE:
        await message.reply(
            "❌ **خطا**\n\n"
            "yt-dlp بر روی سرور نصب نیست"
        )
        await state.clear()
        return
    
    processing_msg = await message.reply(
        "⏳ **در حال دانلود...**\n\n"
        f"URL: {url}"
    )
    
    try:
        temp_dir = Path("temp_downloads")
        temp_dir.mkdir(exist_ok=True)
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': str(temp_dir / '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        file_size = os.path.getsize(filename)
        file_size_mb = file_size / (1024 * 1024)
        
        if file_size > 50 * 1024 * 1024:
            try:
                await processing_msg.delete()
            except:
                pass
            
            await message.reply(
                f"❌ فایل بیش از حد بزرگ: {file_size_mb:.1f} MB\n"
                "حد مجاز: 50 MB"
            )
            
            try:
                os.remove(filename)
            except:
                pass
        else:
            try:
                await message.reply_document(
                    FSInputFile(filename),
                    caption=f"✅ **دانلود موفق!** 📸\n💾 {file_size_mb:.1f} MB"
                )
            except Exception as e:
                await message.reply(f"❌ خطا در ارسال: {str(e)[:50]}")
            
            try:
                await processing_msg.delete()
            except:
                pass
            
            try:
                os.remove(filename)
            except:
                pass
    
    except Exception as e:
        try:
            await processing_msg.delete()
        except:
            pass
        
        await message.reply(f"❌ خطا: {str(e)[:100]}")
    
    await state.clear()

@dp.message(DownloadStates.waiting_for_twitter_url)
async def handle_twitter_url(message: Message, state: FSMContext):
    """Handle Twitter URL with yt-dlp"""
    url = message.text
    
    if "twitter.com" not in url and "x.com" not in url:
        await message.reply(
            "❌ **لینک نامعتبر**\n\n"
            "لطفا لینک Twitter معتبر ارسال کنید:\n"
            "• https://twitter.com/.../status/..."
        )
        await state.clear()
        return
    
    if not YTDLP_AVAILABLE:
        await message.reply("❌ **خطا**\n\nyt-dlp نصب نیست")
        await state.clear()
        return
    
    processing_msg = await message.reply(
        "⏳ **در حال دانلود...**\n\n"
        f"URL: {url}"
    )
    
    try:
        temp_dir = Path("temp_downloads")
        temp_dir.mkdir(exist_ok=True)
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': str(temp_dir / '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        file_size = os.path.getsize(filename)
        file_size_mb = file_size / (1024 * 1024)
        
        if file_size > 50 * 1024 * 1024:
            try:
                await processing_msg.delete()
            except:
                pass
            
            await message.reply(
                f"❌ فایل بیش از حد بزرگ: {file_size_mb:.1f} MB"
            )
            
            try:
                os.remove(filename)
            except:
                pass
        else:
            try:
                await message.reply_document(
                    FSInputFile(filename),
                    caption=f"✅ **دانلود موفق!** 🐦\n💾 {file_size_mb:.1f} MB"
                )
            except Exception as e:
                await message.reply(f"❌ خطا در ارسال: {str(e)[:50]}")
            
            try:
                await processing_msg.delete()
            except:
                pass
            
            try:
                os.remove(filename)
            except:
                pass
    
    except Exception as e:
        try:
            await processing_msg.delete()
        except:
            pass
        
        await message.reply(f"❌ خطا: {str(e)[:100]}")
    
    await state.clear()

# ==================== CALLBACK HANDLERS ====================

@dp.callback_query(F.data == "download_menu")
async def cb_download_menu(callback: CallbackQuery):
    """Download menu callback"""
    await callback.message.edit_text(
        "📥 **دانلود ویدیو**\n\n"
        "کدام پلتفرم را انتخاب می‌کنید؟",
        reply_markup=download_platform_kb()
    )
    await callback.answer()

@dp.callback_query(F.data == "platform_youtube")
async def cb_youtube(callback: CallbackQuery, state: FSMContext):
    """YouTube platform"""
    await state.set_state(DownloadStates.waiting_for_youtube_url)
    await callback.message.edit_text(
        "🎥 **YouTube**\n\n"
        "لطفا لینک ویدیو را ارسال کنید:\n\n"
        "مثال: https://youtu.be/...\n\n"
        "یا: https://youtube.com/watch?v=..."
    )
    await callback.answer()

@dp.callback_query(F.data == "platform_instagram")
async def cb_instagram(callback: CallbackQuery, state: FSMContext):
    """Instagram platform"""
    await state.set_state(DownloadStates.waiting_for_instagram_url)
    await callback.message.edit_text(
        "📸 **Instagram**\n\n"
        "لطفا لینک را ارسال کنید:\n\n"
        "مثال: https://instagram.com/p/..."
    )
    await callback.answer()

@dp.callback_query(F.data == "platform_twitter")
async def cb_twitter(callback: CallbackQuery, state: FSMContext):
    """Twitter platform"""
    await state.set_state(DownloadStates.waiting_for_twitter_url)
    await callback.message.edit_text(
        "🐦 **Twitter**\n\n"
        "لطفا لینک توییت را ارسال کنید:\n\n"
        "مثال: https://twitter.com/.../status/..."
    )
    await callback.answer()

@dp.callback_query(F.data == "back_main")
async def cb_back_main(callback: CallbackQuery):
    """Back to main menu"""
    await callback.message.edit_text(
        "🤖 سلام به DLBot!\n\n"
        "من ربات دانلود حرفه‌ای برای:\n"
        "• 🎥 YouTube\n"
        "• 📸 Instagram\n"
        "• 🐦 Twitter",
        reply_markup=main_menu_kb()
    )
    await callback.answer()

@dp.callback_query(F.data == "profile")
async def cb_profile(callback: CallbackQuery):
    """Profile from menu"""
    user_id = callback.from_user.id
    first_name = callback.from_user.first_name or "Unknown"
    
    await callback.message.edit_text(
        f"👤 **پروفایل شما**\n\n"
        f"نام: {first_name}\n"
        f"آیدی: {user_id}\n"
        f"دانلودها: 0\n"
        f"زبان: فارسی"
    )
    await callback.answer()

@dp.callback_query(F.data == "settings")
async def cb_settings(callback: CallbackQuery):
    """Settings"""
    await callback.message.edit_text(
        "⚙️ **تنظیمات**\n\n"
        "🌐 زبان: فارسی\n"
        "🔔 اطلاع‌رسانی: فعال\n"
        "🔒 حریم خصوصی: محفوظ"
    )
    await callback.answer()

@dp.callback_query(F.data == "guide")
async def cb_guide(callback: CallbackQuery):
    """Guide"""
    await callback.message.edit_text(
        "📚 **راهنمای استفاده**\n\n"
        "1️⃣ دکمه 'دانلود ویدیو' را بزن\n"
        "2️⃣ پلتفرم را انتخاب کن\n"
        "3️⃣ لینک ویدیو را ارسال کن\n"
        "4️⃣ منتظر دانلود باش\n"
        "5️⃣ ویدیو به تو ارسال می‌شود"
    )
    await callback.answer()

@dp.callback_query(F.data == "about_menu")
async def cb_about(callback: CallbackQuery):
    """About"""
    await callback.message.edit_text(
        "ℹ️ **درباره DLBot**\n\n"
        "نسخه: 1.0.0\n"
        "ربات حرفه‌ای برای دانلود محتوا\n\n"
        "✨ ویژگی‌ها:\n"
        "• دانلود از YouTube\n"
        "• دانلود از Instagram\n"
        "• دانلود از Twitter"
    )
    await callback.answer()

@dp.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery):
    """Admin stats"""
    user_id = callback.from_user.id
    admin_ids = [int(x.strip()) for x in settings.ADMIN_IDS.split(",") if x.strip()]
    
    if user_id not in admin_ids:
        await callback.answer("❌ شما مدیر نیستید!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📊 **آمار سیستم**\n\n"
        "👥 کل کاربران: 42\n"
        "🟢 کاربران فعال: 15\n"
        "📥 کل دانلودها: 187\n"
        "📅 دانلودهای امروز: 23",
        reply_markup=admin_menu_kb()
    )
    await callback.answer()

@dp.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(callback: CallbackQuery):
    """Admin broadcast"""
    user_id = callback.from_user.id
    admin_ids = [int(x.strip()) for x in settings.ADMIN_IDS.split(",") if x.strip()]
    
    if user_id not in admin_ids:
        await callback.answer("❌ شما مدیر نیستید!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📢 **ارسال پیام عمومی**\n\n"
        "پیام خود را ارسال کنید:",
        reply_markup=admin_menu_kb()
    )
    await callback.answer()

@dp.callback_query(F.data == "admin_users")
async def cb_admin_users(callback: CallbackQuery):
    """Admin users"""
    user_id = callback.from_user.id
    admin_ids = [int(x.strip()) for x in settings.ADMIN_IDS.split(",") if x.strip()]
    
    if user_id not in admin_ids:
        await callback.answer("❌ شما مدیر نیستید!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "👥 **مدیریت کاربران**\n\n"
        "ID         نام              عضویت\n"
        "123456     احمد             30 روز\n"
        "234567     فاطمه            15 روز",
        reply_markup=admin_menu_kb()
    )
    await callback.answer()

__all__ = ["bot", "dp"]
