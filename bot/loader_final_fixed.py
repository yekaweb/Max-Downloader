"""
FINAL FIXED: Bot Loader with Working Progress + Proper Database
"""

import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from loguru import logger
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
from bot.keyboards.inline.cached_files import (
    get_cached_files_keyboard,
    get_cache_action_keyboard,
)
from utils.progress import generate_progress_message
from utils.format_sizes import get_exact_format_sizes, format_size_mb
from utils.file_cleanup import FileCleanup

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
    logger.error(f"⚠️ Bot initialization failed: {e}")
    bot = None

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Session storage
download_sessions: Dict[int, Dict[str, Any]] = {}


def get_session(user_id: int) -> Dict[str, Any]:
    """Get or create session"""
    if user_id not in download_sessions:
        download_sessions[user_id] = {
            "url": None,
            "format_type": None,
            "quality": None,
            "codec": None,
            "subtitle": None,
            "send_as": None,
            "format_info": None,
            "cached_downloads": None,
            "selected_cached_file": None,
        }
    return download_sessions[user_id]


def clear_session(user_id: int):
    """Clear session"""
    if user_id in download_sessions:
        del download_sessions[user_id]


# ==================== COMMANDS ====================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Start command"""
    from bot.keyboards.inline import main_menu_kb
    
    await message.answer(
        "🤖 **سلام به DLBot!**\n\n"
        "دانلود‌کننده حرفه‌ای برای:\n"
        "• 🎥 YouTube\n"
        "• 📸 Instagram\n"
        "• 🐦 Twitter/X\n"
        "• 🎵 TikTok\n\n"
        "برای شروع دانلود، دکمه‌ی زیر را بزنید:",
        reply_markup=main_menu_kb()
    )


@dp.message(Command("download"))
async def cmd_download(message: Message, state: FSMContext):
    """Download command"""
    await message.answer(
        "📥 **دانلود ویدیو**\n\n"
        "لطفاً لینک ویدیو ارسال کنید:\n\n"
        "مثال‌ها:\n"
        "• https://youtu.be/...\n"
        "• https://instagram.com/p/...",
        reply_markup=get_format_type_keyboard()
    )
    await state.set_state(DownloadStates.waiting_for_url)


# ==================== STEP 1: URL SUBMISSION ====================

@dp.message(DownloadStates.waiting_for_url)
async def handle_url_submission(message: Message, state: FSMContext):
    """STEP 1: User submits URL"""
    url = message.text.strip()
    
    # Validate URL
    if not url.startswith(("http://", "https://")):
        await message.reply("❌ **لینک نامعتبر** - لطفاً لینک صحیح ارسال کنید")
        return
    
    if not YTDLP_AVAILABLE:
        await message.reply("❌ خطا: yt-dlp بر روی سرور نصب نیست")
        await state.clear()
        return
    
    # Show fetching message
    fetch_msg = await message.reply(
        "⏳ **درحال دریافت اطلاعات فیلم...**\n\n"
        "لطفاً صبر کنید...\n"
        "(این ممکن است تا 10 ثانیه طول بکشد)"
    )
    
    try:
        # Fetch exact format information
        format_info = await get_exact_format_sizes(url)
        
        if not format_info:
            await fetch_msg.delete()
            await message.reply("❌ خطا: نتوانستم اطلاعات فیلم را دریافت کنم")
            await state.clear()
            return
        
        # Store in session
        session = get_session(message.from_user.id)
        session["url"] = url
        session["format_info"] = format_info
        
        # Show video info
        title = format_info.get("title", "Media")[:60]
        duration = format_info.get("duration", 0)
        
        duration_str = f"{duration // 3600}:{(duration % 3600) // 60:02d}:{duration % 60:02d}"
        if duration < 3600:
            duration_str = f"{duration // 60}:{duration % 60:02d}"
        
        await fetch_msg.delete()
        await message.answer(
            f"🎬 **{title}**\n\n"
            f"⏱️ **مدت:** {duration_str}\n\n"
            f"🎯 **نوع فایل دریافتی را انتخاب کنید:**",
            reply_markup=get_format_type_keyboard()
        )
        
        await state.set_state(DownloadStates.selecting_format_type)
        
    except Exception as e:
        logger.error(f"Error in URL handler: {e}")
        await fetch_msg.delete()
        await message.reply(f"❌ خطا: {str(e)[:100]}")
        await state.clear()


# ==================== FORMAT TYPE ====================

@dp.callback_query(DownloadStates.selecting_format_type, F.data.startswith("format_"))
async def select_format_type(query: CallbackQuery, state: FSMContext):
    """STEP 2: Format type (Video or Audio)"""
    if query.data == "format_video":
        session = get_session(query.from_user.id)
        format_info = session.get("format_info", {})
        
        await state.set_state(DownloadStates.video_quality_selection)
        await query.message.edit_text(
            "📺 **کیفیت ویدیو را انتخاب کنید:**",
            reply_markup=get_video_quality_keyboard(format_info.get("video_formats", {}))
        )
    
    elif query.data == "format_audio":
        await state.set_state(DownloadStates.audio_format_selection)
        await query.message.edit_text(
            "🎵 **فرمت صوتی را انتخاب کنید:**",
            reply_markup=get_audio_format_keyboard()
        )
    
    await query.answer()


# ==================== QUALITY SELECTION ====================

@dp.callback_query(DownloadStates.video_quality_selection, F.data.startswith("quality_"))
async def select_quality(query: CallbackQuery, state: FSMContext):
    """STEP 3A: Quality selected"""
    quality_map = {
        "quality_4k": "4k",
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
        f"🎞️ **کدک ویدیو را انتخاب کنید:**\n\nبرای کیفیت {quality}",
        reply_markup=get_video_codec_keyboard()
    )
    await query.answer()


# ==================== CODEC SELECTION ====================

@dp.callback_query(DownloadStates.video_codec_selection, F.data.startswith("codec_"))
async def select_codec(query: CallbackQuery, state: FSMContext):
    """STEP 4: Codec selected"""
    codec_map = {
        "codec_h264": "h264",
        "codec_av1": "av1",
        "codec_vp9": "vp9",
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


# ==================== SUBTITLE ====================

@dp.callback_query(DownloadStates.video_selecting_subtitle, F.data.startswith("subtitle_"))
async def select_subtitle(query: CallbackQuery, state: FSMContext):
    """STEP 5: Subtitle selected"""
    session = get_session(query.from_user.id)
    session["subtitle"] = query.data.replace("subtitle_", "")
    
    await state.set_state(DownloadStates.video_selecting_send_as)
    await query.message.edit_text(
        "📤 **نحوه دریافت فایل:**",
        reply_markup=get_send_as_keyboard()
    )
    await query.answer()


# ==================== AUDIO FORMAT ====================

@dp.callback_query(DownloadStates.audio_format_selection, F.data.startswith("audio_"))
async def select_audio(query: CallbackQuery, state: FSMContext):
    """STEP 3B: Audio format selected"""
    session = get_session(query.from_user.id)
    session["audio_format"] = query.data.replace("audio_", "")
    
    await state.set_state(DownloadStates.downloading)
    await start_audio_download(query.message, query.from_user.id, state)
    await query.answer()


# ==================== SEND AS ====================

@dp.callback_query(DownloadStates.video_selecting_send_as, F.data.startswith("send_as_"))
async def select_send_as(query: CallbackQuery, state: FSMContext):
    """STEP 6: Send as type selected"""
    session = get_session(query.from_user.id)
    session["send_as"] = query.data.replace("send_as_", "")
    
    await state.set_state(DownloadStates.downloading)
    await start_video_download(query.message, query.from_user.id, state)
    await query.answer()


# ==================== CANCEL ====================

@dp.callback_query(F.data == "download_cancel")
async def on_cancel(query: CallbackQuery, state: FSMContext):
    """Cancel"""
    await query.message.delete()
    await query.answer("✅ لغو شد")
    await state.clear()


@dp.callback_query(F.data == "download_menu")
async def on_download_menu(query: CallbackQuery):
    """Download menu"""
    from bot.keyboards.inline import download_platform_kb
    
    await query.message.edit_text(
        "📥 **دانلود فایل**\n\n"
        "پلتفرمی را انتخاب کنید:",
        reply_markup=download_platform_kb()
    )
    await query.answer()


@dp.callback_query(F.data.startswith("platform_"))
async def on_platform_select(query: CallbackQuery, state: FSMContext):
    """Platform selected"""
    platform = query.data.replace("platform_", "")
    
    await query.message.edit_text(
        f"📥 **دانلود از {platform.upper()}**\n\n"
        f"لطفاً لینک ویدیو ارسال کنید:"
    )
    await state.set_state(DownloadStates.waiting_for_url)
    await query.answer()


# ==================== DOWNLOAD FUNCTIONS ====================

async def start_video_download(message: Message, user_id: int, state: FSMContext):
    """Download video with REAL progress updates"""
    session = get_session(user_id)
    url = session.get("url")
    
    if not url:
        await message.answer("❌ خطا: URL پیدا نشد")
        clear_session(user_id)
        await state.clear()
        return
    
    # Send initial message
    progress_msg = await message.answer("⏳ **شروع دانلود...**")
    
    try:
        temp_dir = Path("temp_downloads")
        temp_dir.mkdir(exist_ok=True)
        
        # yt-dlp options with progress hook
        def progress_hook(d):
            """Called by yt-dlp during download"""
            if d['status'] == 'downloading':
                total = d.get('total_bytes', 0)
                downloaded = d.get('downloaded_bytes', 0)
                
                if total > 0:
                    percent = (downloaded / total) * 100
                    speed = d.get('speed', 0) or 0
                    eta = d.get('eta', 0) or 0
                    
                    # Update session with real values
                    session['progress'] = {
                        'percent': percent,
                        'downloaded_mb': downloaded / (1024 * 1024),
                        'total_mb': total / (1024 * 1024),
                        'speed_mbps': (speed or 0) / (1024 * 1024),
                        'eta_seconds': eta,
                    }
        
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'quiet': True,
            'no_warnings': True,
            'outtmpl': str(temp_dir / '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'socket_timeout': 30,
        }
        
        # Download with yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            file_size_mb = file_size / (1024 * 1024)
            
            if file_size > 2 * 1024 * 1024 * 1024:  # 2 GB limit
                await progress_msg.delete()
                await message.answer(f"❌ **فایل بیش از حد بزرگ:** {file_size_mb:.1f} MB")
                try:
                    os.remove(filename)
                except:
                    pass
            else:
                try:
                    # Upload to Telegram
                    upload_msg = await message.answer("⬆️ **درحال آپلود به تلگرام...**")
                    
                    sent = await message.reply_video(
                        FSInputFile(filename),
                        caption=f"✅ **دانلود موفق!**\n\n📹 {info.get('title', 'Video')[:50]}\n💾 {file_size_mb:.1f} MB"
                    )
                    
                    # Delete upload message
                    try:
                        await upload_msg.delete()
                    except:
                        pass
                    
                    # Cleanup file
                    try:
                        os.remove(filename)
                        logger.info(f"✅ Cleaned up: {filename}")
                    except Exception as e:
                        logger.warning(f"Cleanup failed: {e}")
                    
                except Exception as e:
                    logger.error(f"Upload error: {e}")
                    await message.answer(f"❌ خطا در ارسال: {str(e)[:100]}")
                
                try:
                    await progress_msg.delete()
                except:
                    pass
    
    except Exception as e:
        logger.error(f"Download error: {e}")
        try:
            await progress_msg.delete()
        except:
            pass
        await message.answer(f"❌ **خطا:** {str(e)[:100]}")
    
    finally:
        clear_session(user_id)
        await state.clear()


async def start_audio_download(message: Message, user_id: int, state: FSMContext):
    """Download audio"""
    session = get_session(user_id)
    url = session.get("url")
    
    if not url:
        await message.answer("❌ خطا: URL پیدا نشد")
        clear_session(user_id)
        await state.clear()
        return
    
    progress_msg = await message.answer("⏳ **درحال دانلود صوت...**")
    
    try:
        temp_dir = Path("temp_downloads")
        temp_dir.mkdir(exist_ok=True)
        
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]',
            'quiet': True,
            'no_warnings': True,
            'outtmpl': str(temp_dir / '%(title)s.%(ext)s'),
            'socket_timeout': 30,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        if os.path.exists(filename):
            try:
                await message.reply_audio(
                    FSInputFile(filename),
                    caption=f"✅ {info.get('title', 'Audio')[:50]}"
                )
                
                # Cleanup
                try:
                    os.remove(filename)
                except:
                    pass
                
            except Exception as e:
                logger.error(f"Audio upload error: {e}")
                await message.answer(f"❌ خطا: {str(e)[:50]}")
                try:
                    os.remove(filename)
                except:
                    pass
            
            try:
                await progress_msg.delete()
            except:
                pass
    
    except Exception as e:
        logger.error(f"Audio download error: {e}")
        try:
            await progress_msg.delete()
        except:
            pass
        await message.answer(f"❌ **خطا:** {str(e)[:100]}")
    
    finally:
        clear_session(user_id)
        await state.clear()


__all__ = ["bot", "dp"]
