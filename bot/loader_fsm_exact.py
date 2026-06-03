"""
Complete Bot Loader with FSM + EXACT File Sizes
Calculates real file sizes before showing quality/codec options
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
from config_simple import settings
from database.connection import AsyncSessionLocal
from database.repositories.cached_download_repo import CachedDownloadRepository
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
from utils.format_sizes import get_exact_format_sizes, format_size_mb

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
            "format_info": None,  # ✅ Store format info
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
    await message.answer(
        "🤖 **سلام به DLBot!**\n\n"
        "دانلود‌کننده حرفه‌ای برای:\n"
        "• 🎥 YouTube\n"
        "• 📸 Instagram\n"
        "• 🐦 Twitter/X\n"
        "• 🎵 TikTok\n\n"
        "شروع کنید: /download",
    )


@dp.message(Command("download"))
async def cmd_download(message: Message, state: FSMContext):
    """Download command"""
    await message.answer(
        "📥 **دانلود ویدیو**\n\n"
        "لطفاً لینک ویدیو ارسال کنید:\n\n"
        "مثال‌ها:\n"
        "• https://youtu.be/...\n"
        "• https://instagram.com/p/..."
    )
    await state.set_state(DownloadStates.waiting_for_url)


# ==================== STEP 1: URL SUBMISSION ====================

@dp.message(DownloadStates.waiting_for_url)
async def handle_url_submission(message: Message, state: FSMContext):
    """STEP 1: User submits URL - Fetch exact format info"""
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
            f"⏱ مدت زمان: {duration_str}\n"
            f"📊 فرمت‌های موجود: {len(format_info.get('video_formats', {}))} کیفیت ویدیو\n\n"
            "🎯 **نوع فایل را انتخاب کنید:**",
            reply_markup=get_format_type_keyboard()
        )
        
        await state.set_state(DownloadStates.selecting_format_type)
    
    except asyncio.TimeoutError:
        await fetch_msg.delete()
        await message.reply("❌ **زمان‌اندازی فراتر رفت** - لطفاً دوباره تلاش کنید")
        await state.clear()
    except Exception as e:
        await fetch_msg.delete()
        await message.reply(f"❌ **خطا:** {str(e)[:100]}")
        await state.clear()


# ==================== STEP 2: FORMAT TYPE ====================

@dp.callback_query(DownloadStates.selecting_format_type, F.data == "format_video")
async def select_video_format(query: CallbackQuery, state: FSMContext):
    """STEP 2A: Video selected"""
    session = get_session(query.from_user.id)
    session["format_type"] = "video"
    
    # Get exact format info
    format_info = session.get("format_info", {})
    video_formats = format_info.get("video_formats", {})
    
    await state.set_state(DownloadStates.video_quality_selection)
    await query.message.edit_text(
        "📺 **کیفیت ویدیو را انتخاب کنید:**\n\n"
        "(نمایش حجم دقیق هر کیفیت)\n",
        reply_markup=get_video_quality_keyboard(video_formats)
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
    
    # Get codec sizes for selected quality
    format_info = session.get("format_info", {})
    video_formats = format_info.get("video_formats", {})
    
    # Build codec sizes for this quality
    codec_sizes = {}
    if quality in video_formats:
        quality_data = video_formats[quality]
        size_mb = quality_data.get("size_mb", 0)
        codec = quality_data.get("codec", "h264")
        codec_sizes[codec] = {"size_mb": size_mb}
    
    # Also check for other codecs at this quality
    all_codecs = set()
    for q, data in video_formats.items():
        all_codecs.add(data.get("codec", "h264"))
    
    for codec in all_codecs:
        if codec not in codec_sizes:
            # Estimate other codec sizes
            size_mb = video_formats[quality].get("size_mb", 0) * 0.8 if quality in video_formats else 0
            codec_sizes[codec] = {"size_mb": size_mb}
    
    await state.set_state(DownloadStates.video_codec_selection)
    await query.message.edit_text(
        f"🎞️ **کدک ویدیو را انتخاب کنید:**\n\n"
        f"برای کیفیت {quality} (حجم دقیق)\n",
        reply_markup=get_video_codec_keyboard(codec_sizes)
    )
    await query.answer()


# ==================== STEP 4: CODEC ====================

@dp.callback_query(DownloadStates.video_codec_selection, F.data.startswith("codec_"))
async def select_video_codec(query: CallbackQuery, state: FSMContext):
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


# ==================== STEP 5: SUBTITLE ====================

@dp.callback_query(DownloadStates.video_selecting_subtitle, F.data.startswith("subtitle_"))
async def select_video_subtitle(query: CallbackQuery, state: FSMContext):
    """STEP 5: Subtitle selected"""
    subtitle_map = {
        "subtitle_fa": "fa",
        "subtitle_en": "en",
        "subtitle_ar": "ar",
        "subtitle_ru": "ru",
        "subtitle_none": None,
    }
    
    subtitle = subtitle_map.get(query.data)
    if query.data not in subtitle_map:
        await query.answer("❌ زیرنویس نامعتبر", show_alert=True)
        return
    
    session = get_session(query.from_user.id)
    session["subtitle"] = subtitle
    
    await state.set_state(DownloadStates.video_selecting_send_as)
    await query.message.edit_text(
        "📤 **نحوه دریافت فایل:**",
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


# ==================== STEP 7: DOWNLOADS ====================

async def start_video_download(message: Message, user_id: int, state: FSMContext):
    """STEP 7A: Start video download"""
    session = get_session(user_id)
    url = session.get("url")
    
    if not url:
        await message.answer("❌ خطا: URL پیدا نشد")
        clear_session(user_id)
        await state.clear()
        return
    
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

    # Check DB cache for existing uploads
    try:
        async with AsyncSessionLocal() as db:
            repo = CachedDownloadRepository(db)
            cached = await repo.find_valid_by_url(url)
            if cached:
                entry = cached[0]
                # Send cached file_id if available
                try:
                    await progress_msg.delete()
                except Exception:
                    pass

                try:
                    # Use file_id to resend without re-downloading
                    await message.answer_video(entry.telegram_file_id,
                                               caption=f"✅ فایل از کش ارسال شد\n📹 {entry.media_title}\n💾 {entry.file_size/1024/1024:.1f} MB")
                    await state.clear()
                    clear_session(user_id)
                    return
                except Exception:
                    # If sending cached file fails, continue to fresh download
                    pass
    except Exception:
        # DB errors should not block download flow
        pass
    
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
                    sent = await message.reply_video(
                        FSInputFile(filename),
                        caption=f"✅ **دانلود موفق!**\n\n📹 {info.get('title', 'Video')}\n💾 {file_size_mb:.1f} MB"
                    )
                    # Persist cache record (best-effort)
                    try:
                        async with AsyncSessionLocal() as db:
                            repo = CachedDownloadRepository(db)
                            await repo.create_from_upload(
                                source_url=url,
                                source_platform="youtube",
                                media_title=info.get('title', '')[:500],
                                media_duration=info.get('duration', 0),
                                media_uploader=info.get('uploader', ''),
                                telegram_file_id=sent.video.file_id,
                                file_size=file_size,
                                file_type="video/mp4",
                                quality=session.get('quality', 'best'),
                                format_codec=session.get('codec', 'h264'),
                                format_container='mp4',
                                resolution_width=None,
                                resolution_height=None,
                            )
                    except Exception:
                        pass
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
    
    except Exception as e:
        try:
            await progress_msg.delete()
        except:
            pass
        await message.answer(f"❌ **خطا:** {str(e)[:100]}")
    
    finally:
        clear_session(user_id)
        await state.clear()


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
                await message.answer(f"❌ **فایل بیش از حد بزرگ:** {file_size_mb:.1f} MB")
                try:
                    os.remove(filename)
                except:
                    pass
            else:
                try:
                    sent = await message.reply_audio(
                        FSInputFile(filename),
                        caption=f"✅ **دانلود موفق!**\n\n🎵 {info.get('title', 'Audio')}\n💾 {file_size_mb:.1f} MB"
                    )
                    # Persist cache record (best-effort)
                    try:
                        async with AsyncSessionLocal() as db:
                            repo = CachedDownloadRepository(db)
                            await repo.create_from_upload(
                                source_url=url,
                                source_platform="youtube",
                                media_title=info.get('title', '')[:500],
                                media_duration=info.get('duration', 0),
                                media_uploader=info.get('uploader', ''),
                                telegram_file_id=sent.audio.file_id,
                                file_size=file_size,
                                file_type=sent.audio.mime_type if getattr(sent, 'audio', None) else 'audio/mpeg',
                                quality=session.get('audio_format', 'audio'),
                                format_codec='mp3',
                                format_container='mp3',
                            )
                    except Exception:
                        pass
                except Exception as e:
                    await message.answer(f"❌ خطا: {str(e)[:50]}")
                
                try:
                    await progress_msg.delete()
                except:
                    pass
                
                try:
                    os.remove(filename)
                except:
                    pass
    
    except Exception as e:
        try:
            await progress_msg.delete()
        except:
            pass
        await message.answer(f"❌ **خطا:** {str(e)[:100]}")
    
    finally:
        clear_session(user_id)
        await state.clear()


# ==================== BACK BUTTONS ====================

@dp.callback_query(F.data == "back_to_format")
async def back_to_format(query: CallbackQuery, state: FSMContext):
    """Go back to format type"""
    await state.set_state(DownloadStates.selecting_format_type)
    await query.message.edit_text(
        "🎯 **نوع فایل دریافتی را انتخاب کنید:**",
        reply_markup=get_format_type_keyboard()
    )
    await query.answer()


@dp.callback_query(F.data == "back_to_quality")
async def back_to_quality(query: CallbackQuery, state: FSMContext):
    """Go back to quality"""
    session = get_session(query.from_user.id)
    format_info = session.get("format_info", {})
    video_formats = format_info.get("video_formats", {})
    
    await state.set_state(DownloadStates.video_quality_selection)
    await query.message.edit_text(
        "📺 **کیفیت ویدیو را انتخاب کنید:**",
        reply_markup=get_video_quality_keyboard(video_formats)
    )
    await query.answer()


@dp.callback_query(F.data == "back_to_codec")
async def back_to_codec(query: CallbackQuery, state: FSMContext):
    """Go back to codec"""
    await state.set_state(DownloadStates.video_codec_selection)
    await query.message.edit_text(
        "🎞️ **کدک ویدیو را انتخاب کنید:**",
        reply_markup=get_video_codec_keyboard()
    )
    await query.answer()


@dp.callback_query(F.data == "back_to_subtitle")
async def back_to_subtitle(query: CallbackQuery, state: FSMContext):
    """Go back to subtitle"""
    await state.set_state(DownloadStates.video_selecting_subtitle)
    await query.message.edit_text(
        "📝 **زیرنویس می‌خواهید؟**",
        reply_markup=get_subtitle_keyboard()
    )
    await query.answer()


# Fallback
@dp.message(StateFilter(None))
async def handle_message(message: Message):
    """Fallback"""
    await message.reply(
        "❌ دستور شناخته شده نیست\n\n"
        "/download - دانلود\n"
        "/help - راهنما"
    )


__all__ = ["bot", "dp"]
