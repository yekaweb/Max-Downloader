"""Complete Bot Loader with Full FSM Download Flow - All handlers integrated"""

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
from bot.states.download import DownloadStates
from bot.keyboards.inline.download import (
    get_format_type_keyboard,
    get_video_quality_keyboard,
    get_video_codec_keyboard,
    get_subtitle_keyboard,
    get_send_as_keyboard,
    get_audio_format_keyboard,
)
from utils.progress import generate_progress_message

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
    print(f"⚠️ Bot initialization failed: {e}")
    bot = None

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Session storage for download process
download_sessions = {}


def get_session(user_id: int):
    """Get or create session"""
    if user_id not in download_sessions:
        download_sessions[user_id] = {}
    return download_sessions[user_id]


def clear_session(user_id: int):
    """Clear session"""
    if user_id in download_sessions:
        del download_sessions[user_id]


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
        [InlineKeyboardButton(text="📨 دانلود به روش جدید", callback_data="new_download")],
        [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_main")]
    ])


# ==================== COMMANDS ====================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Start command"""
    await message.answer(
        "🤖 **سلام به DLBot!**\n\n"
        "من ربات دانلود حرفه‌ای برای:\n"
        "• 🎥 YouTube\n"
        "• 📸 Instagram\n"
        "• 🐦 Twitter/X\n"
        "• 🎵 TikTok\n\n"
        "برای شروع دکمه پایین را بزن!",
        reply_markup=main_menu_kb()
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Help command"""
    await message.answer(
        "📖 **دستورات موجود:**\n\n"
        "/start - شروع\n"
        "/help - راهنما\n"
        "/download - دانلود ویدیو\n\n"
        "**چگونه استفاده کنید:**\n\n"
        "1️⃣ دکمه 'دانلود ویدیو' را بزنید\n"
        "2️⃣ لینک ویدیو را ارسال کنید\n"
        "3️⃣ نوع فایل انتخاب کنید (ویدیو/صدا)\n"
        "4️⃣ کیفیت و فرمت انتخاب کنید\n"
        "5️⃣ ربات برای شما دانلود می‌کند! 🎉"
    )


@dp.message(Command("download"))
async def cmd_download(message: Message, state: FSMContext):
    """Download command"""
    await message.answer(
        "📥 **دانلود ویدیو**\n\n"
        "لطفاً یک لینک ویدیو ارسال کنید:\n\n"
        "مثال‌ها:\n"
        "• https://youtu.be/...\n"
        "• https://instagram.com/p/...\n"
        "• https://twitter.com/...",
    )
    await state.set_state(DownloadStates.waiting_for_url)


# ==================== STEP 1: URL SUBMISSION ====================

@dp.message(DownloadStates.waiting_for_url)
async def handle_url_submission(message: Message, state: FSMContext):
    """STEP 1: User submits URL"""
    url = message.text.strip()
    
    # Validate URL format
    if not url.startswith(("http://", "https://")):
        await message.reply("❌ **لینک نامعتبر** - لطفاً لینک صحیح ارسال کنید")
        return
    
    if not YTDLP_AVAILABLE:
        await message.reply("❌ خطا: yt-dlp بر روی سرور نصب نیست")
        await state.clear()
        return
    
    # Store URL
    session = get_session(message.from_user.id)
    session["url"] = url
    
    # Move to format type selection
    await state.set_state(DownloadStates.selecting_format_type)
    await message.answer(
        "🎯 **نوع فایل دریافتی را انتخاب کنید:**\n\n"
        "• 🎬 ویدیو - دانلود با کیفیت انتخابی\n"
        "• 🎵 صدا - فقط صدا را استخراج کنید",
        reply_markup=get_format_type_keyboard()
    )


# ==================== STEP 2: FORMAT TYPE ====================

@dp.callback_query(DownloadStates.selecting_format_type, F.data == "format_video")
async def select_video_format(query: CallbackQuery, state: FSMContext):
    """STEP 2A: Video selected"""
    session = get_session(query.from_user.id)
    session["format_type"] = "video"
    
    await state.set_state(DownloadStates.video_quality_selection)
    await query.message.edit_text(
        "📺 **کیفیت ویدیو را انتخاب کنید:**\n\n"
        "━━━━ کیفیت بالا ━━━━\n"
        "🔵 4K (2160p) • ~2.1GB\n"
        "🟢 1080p • ~850MB\n\n"
        "━━━━ کیفیت متوسط ━━━━\n"
        "🟡 720p • ~420MB ✅ پیشنهاد\n"
        "🟠 480p • ~200MB\n\n"
        "━━━━ کیفیت پایین ━━━━\n"
        "🔴 360p • ~95MB\n"
        "⚫ 240p • ~45MB",
        reply_markup=get_video_quality_keyboard()
    )
    await query.answer()


@dp.callback_query(DownloadStates.selecting_format_type, F.data == "format_audio")
async def select_audio_format(query: CallbackQuery, state: FSMContext):
    """STEP 2B: Audio selected"""
    session = get_session(query.from_user.id)
    session["format_type"] = "audio"
    
    await state.set_state(DownloadStates.audio_format_selection)
    await query.message.edit_text(
        "🎵 **فرمت صوتی را انتخاب کنید:**",
        reply_markup=get_audio_format_keyboard()
    )
    await query.answer()


# ==================== STEP 3A: VIDEO QUALITY ====================

@dp.callback_query(DownloadStates.video_quality_selection, F.data.startswith("quality_"))
async def select_video_quality(query: CallbackQuery, state: FSMContext):
    """STEP 3A: Video quality selected"""
    quality_map = {
        "quality_4k": "2160p",
        "quality_1080": "1080p",
        "quality_720": "720p",
        "quality_480": "480p",
        "quality_360": "360p",
        "quality_240": "240p",
    }
    
    quality = quality_map.get(query.data)
    if not quality:
        await query.answer("❌ کیفیت نامعتبر", show_alert=True)
        return
    
    session = get_session(query.from_user.id)
    session["quality"] = quality
    
    await state.set_state(DownloadStates.video_codec_selection)
    await query.message.edit_text(
        "🎞️ **کدک ویدیو را انتخاب کنید:**\n\n"
        "• H.264 | MP4 ✅ سازگار با همه دستگاه‌ها\n"
        "• AV1 | WebM 🏆 بهترین کیفیت/حجم\n"
        "• VP9 | WebM ⚡ سبک و کارآمد\n\n"
        "<i>ℹ️ اگر مطمئن نیستید H.264 را انتخاب کنید</i>",
        reply_markup=get_video_codec_keyboard()
    )
    await query.answer()


# ==================== STEP 4: CODEC ====================

@dp.callback_query(DownloadStates.video_codec_selection, F.data.startswith("codec_"))
async def select_video_codec(query: CallbackQuery, state: FSMContext):
    """STEP 4: Codec selected"""
    codec_map = {
        "codec_h264": "H.264",
        "codec_av1": "AV1",
        "codec_vp9": "VP9",
    }
    
    codec = codec_map.get(query.data)
    if not codec:
        await query.answer("❌ کدک نامعتبر", show_alert=True)
        return
    
    session = get_session(query.from_user.id)
    session["codec"] = codec
    
    await state.set_state(DownloadStates.video_selecting_subtitle)
    await query.message.edit_text(
        "📝 **زیرنویس می‌خواهید؟**",
        reply_markup=get_subtitle_keyboard()
    )
    await query.answer()


# ==================== STEP 5: SUBTITLE ====================

@dp.callback_query(DownloadStates.video_selecting_subtitle, F.data.startswith("subtitle_"))
async def select_video_subtitle(query: CallbackQuery, state: FSMContext):
    """STEP 5: Subtitle selected"""
    subtitle_map = {
        "subtitle_fa": "فارسی",
        "subtitle_en": "English",
        "subtitle_ar": "عربی",
        "subtitle_ru": "Русский",
        "subtitle_none": "نه",
    }
    
    subtitle = subtitle_map.get(query.data)
    if not subtitle:
        await query.answer("❌ زیرنویس نامعتبر", show_alert=True)
        return
    
    session = get_session(query.from_user.id)
    session["subtitle"] = subtitle
    
    await state.set_state(DownloadStates.video_selecting_send_as)
    await query.message.edit_text(
        "📤 **نحوه دریافت فایل:**\n\n"
        "• 📹 ویدیو - قابل پخش در تلگرام\n"
        "• 📁 فایل - دانلود کامل",
        reply_markup=get_send_as_keyboard()
    )
    await query.answer()


# ==================== STEP 6: SEND AS ====================

@dp.callback_query(DownloadStates.video_selecting_send_as, F.data.startswith("send_as_"))
async def select_send_as(query: CallbackQuery, state: FSMContext):
    """STEP 6: Send As selected - Start download"""
    send_as_map = {
        "send_as_video": "video",
        "send_as_file": "file",
    }
    
    send_as = send_as_map.get(query.data)
    if not send_as:
        await query.answer("❌ گزینه نامعتبر", show_alert=True)
        return
    
    session = get_session(query.from_user.id)
    session["send_as"] = send_as
    
    await state.set_state(DownloadStates.downloading)
    await start_video_download(query.message, query.from_user.id, state)


# ==================== STEP 3B: AUDIO FORMAT ====================

@dp.callback_query(DownloadStates.audio_format_selection, F.data.startswith("audio_"))
async def select_audio_format_type(query: CallbackQuery, state: FSMContext):
    """STEP 3B: Audio format selected - Start download"""
    audio_map = {
        "audio_mp3_320": "MP3 320kbps",
        "audio_mp3_128": "MP3 128kbps",
        "audio_aac_256": "AAC 256kbps",
        "audio_m4a_128": "M4A 128kbps",
        "audio_opus": "OPUS",
    }
    
    audio_fmt = audio_map.get(query.data)
    if not audio_fmt:
        await query.answer("❌ فرمت نامعتبر", show_alert=True)
        return
    
    session = get_session(query.from_user.id)
    session["audio_format"] = audio_fmt
    
    await state.set_state(DownloadStates.downloading)
    await start_audio_download(query.message, query.from_user.id, state)


# ==================== STEP 7A: VIDEO DOWNLOAD ====================

async def start_video_download(message: Message, user_id: int, state: FSMContext):
    """STEP 7A: Start video download"""
    session = get_session(user_id)
    url = session.get("url")
    
    if not url:
        await message.answer("❌ خطا: URL پیدا نشد")
        clear_session(user_id)
        await state.clear()
        return
    
    # Show progress
    progress_msg = await message.answer(
        generate_progress_message(
            title="شروع دانلود...",
            progress_percent=0,
            downloaded_mb=0,
            total_mb=1,
            speed_mbps=0,
            eta_seconds=0,
            phase="download"
        ),
        parse_mode="HTML"
    )
    
    try:
        temp_dir = Path("temp_downloads")
        temp_dir.mkdir(exist_ok=True)
        
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'quiet': True,
            'no_warnings': True,
            'outtmpl': str(temp_dir / '%(title)s.%(ext)s'),
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            file_size_mb = file_size / (1024 * 1024)
            
            if file_size > 50 * 1024 * 1024:
                await progress_msg.delete()
                await message.answer(f"❌ **فایل بیش از حد بزرگ:** {file_size_mb:.1f} MB (حد: 50 MB)")
                try:
                    os.remove(filename)
                except:
                    pass
            else:
                try:
                    await message.reply_video(
                        FSInputFile(filename),
                        caption=f"✅ **دانلود موفق!**\n\n📹 {info.get('title', 'Video')}\n💾 {file_size_mb:.1f} MB"
                    )
                except Exception as e:
                    await message.answer(f"❌ خطا در ارسال: {str(e)[:50]}")
                
                try:
                    await progress_msg.delete()
                except:
                    pass
                
                try:
                    os.remove(filename)
                except:
                    pass
        else:
            await message.answer("❌ فایل دانلود شده پیدا نشد")
    
    except Exception as e:
        try:
            await progress_msg.delete()
        except:
            pass
        await message.answer(f"❌ **خطا:** {str(e)[:100]}")
    
    finally:
        clear_session(user_id)
        await state.clear()


# ==================== STEP 7B: AUDIO DOWNLOAD ====================

async def start_audio_download(message: Message, user_id: int, state: FSMContext):
    """STEP 7B: Start audio download"""
    session = get_session(user_id)
    url = session.get("url")
    
    if not url:
        await message.answer("❌ خطا: URL پیدا نشد")
        clear_session(user_id)
        await state.clear()
        return
    
    progress_msg = await message.answer(
        generate_progress_message(
            title="استخراج صدا...",
            progress_percent=0,
            downloaded_mb=0,
            total_mb=1,
            speed_mbps=0,
            eta_seconds=0,
            phase="download"
        ),
        parse_mode="HTML"
    )
    
    try:
        temp_dir = Path("temp_downloads")
        temp_dir.mkdir(exist_ok=True)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'outtmpl': str(temp_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # For audio, file might have different extension after processing
            base_name = str(temp_dir / Path(filename).stem)
            for ext in ['.mp3', '.m4a', '.opus', '.aac']:
                if os.path.exists(base_name + ext):
                    filename = base_name + ext
                    break
        
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            file_size_mb = file_size / (1024 * 1024)
            
            if file_size > 50 * 1024 * 1024:
                await progress_msg.delete()
                await message.answer(f"❌ **فایل بیش از حد بزرگ:** {file_size_mb:.1f} MB (حد: 50 MB)")
                try:
                    os.remove(filename)
                except:
                    pass
            else:
                try:
                    await message.reply_audio(
                        FSInputFile(filename),
                        caption=f"✅ **دانلود موفق!**\n\n🎵 {info.get('title', 'Audio')}\n💾 {file_size_mb:.1f} MB"
                    )
                except Exception as e:
                    await message.answer(f"❌ خطا در ارسال: {str(e)[:50]}")
                
                try:
                    await progress_msg.delete()
                except:
                    pass
                
                try:
                    os.remove(filename)
                except:
                    pass
        else:
            await message.answer("❌ فایل دانلود شده پیدا نشد")
    
    except Exception as e:
        try:
            await progress_msg.delete()
        except:
            pass
        await message.answer(f"❌ **خطا:** {str(e)[:100]}")
    
    finally:
        clear_session(user_id)
        await state.clear()


# ==================== CALLBACK HANDLERS ====================

@dp.callback_query(F.data == "download_menu")
async def handle_download_menu(query: CallbackQuery, state: FSMContext):
    """Download menu callback"""
    await state.set_state(DownloadStates.waiting_for_url)
    await query.message.edit_text(
        "📥 **دانلود ویدیو**\n\n"
        "لطفاً یک لینک ویدیو ارسال کنید:\n\n"
        "مثال‌ها:\n"
        "• https://youtu.be/...\n"
        "• https://instagram.com/p/...",
    )
    await query.answer()


@dp.callback_query(F.data == "cancel_download")
async def cancel_download(query: CallbackQuery, state: FSMContext):
    """Cancel download"""
    clear_session(query.from_user.id)
    await state.clear()
    await query.message.delete()
    await query.answer("❌ دانلود لغو شد")


# Back buttons
@dp.callback_query(F.data == "back_to_format")
async def back_to_format(query: CallbackQuery, state: FSMContext):
    """Back to format"""
    await state.set_state(DownloadStates.selecting_format_type)
    await query.message.edit_text(
        "🎯 **نوع فایل دریافتی را انتخاب کنید:**",
        reply_markup=get_format_type_keyboard()
    )
    await query.answer()


@dp.callback_query(F.data.in_(["back_to_quality", "back_to_codec", "back_to_subtitle"]))
async def back_button(query: CallbackQuery, state: FSMContext):
    """Back buttons"""
    current_state = await state.get_state()
    
    if query.data == "back_to_quality" and current_state == DownloadStates.video_codec_selection:
        await state.set_state(DownloadStates.video_quality_selection)
        await query.message.edit_text(
            "📺 **کیفیت ویدیو را انتخاب کنید:**",
            reply_markup=get_video_quality_keyboard()
        )
    elif query.data == "back_to_codec" and current_state == DownloadStates.video_selecting_subtitle:
        await state.set_state(DownloadStates.video_codec_selection)
        await query.message.edit_text(
            "🎞️ **کدک ویدیو را انتخاب کنید:**",
            reply_markup=get_video_codec_keyboard()
        )
    elif query.data == "back_to_subtitle" and current_state == DownloadStates.video_selecting_send_as:
        await state.set_state(DownloadStates.video_selecting_subtitle)
        await query.message.edit_text(
            "📝 **زیرنویس می‌خواهید؟**",
            reply_markup=get_subtitle_keyboard()
        )
    
    await query.answer()


# Fallback
@dp.message(StateFilter(None))
async def handle_message(message: Message):
    """Fallback handler"""
    await message.reply(
        "❌ دستور شناخته شده نیست\n\n"
        "برای دانلود: /download\n"
        "برای راهنما: /help\n"
        "برای شروع: /start"
    )


__all__ = ["bot", "dp"]
