"""
Complete download handler with step-by-step FSM flow
STEP 1: URL → STEP 2: Format Type → STEP 3-4: Quality/Codec → STEP 5: Subtitles → STEP 6: Send As → Download
"""

import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, Command
from bot.states.download import DownloadStates
from bot.keyboards.inline.download import (
    get_format_type_keyboard,
    get_video_quality_keyboard,
    get_video_codec_keyboard,
    get_subtitle_keyboard,
    get_send_as_keyboard,
    get_audio_format_keyboard,
)
from config import settings
from utils.progress import generate_progress_message
from utils.safe_error import safe_user_message

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False

router = Router()

# Temporary storage for download session data
download_sessions: Dict[int, Dict[str, Any]] = {}


def get_session(user_id: int) -> Dict[str, Any]:
    """Get or create session data for user"""
    if user_id not in download_sessions:
        download_sessions[user_id] = {
            "url": None,
            "format_type": None,  # "video" or "audio"
            "quality": None,
            "codec": None,
            "subtitle": None,
            "send_as": None,  # "video" or "file"
        }
    return download_sessions[user_id]


def clear_session(user_id: int):
    """Clear session data after download"""
    if user_id in download_sessions:
        del download_sessions[user_id]


# ==================== STEP 1: URL SUBMISSION ====================

@router.message(DownloadStates.waiting_for_url)
async def handle_url_submission(message: Message, state: FSMContext):
    """STEP 1: User submits URL"""
    url = message.text.strip()
    
    # Validate URL format
    if not url.startswith(("http://", "https://")):
        await message.reply(
            "❌ **لینک نامعتبر**\n\n"
            "لطفاً یک لینک معتبر شامل http:// یا https:// ارسال کنید"
        )
        return
    
    if not YTDLP_AVAILABLE:
        await message.reply("❌ خطا: yt-dlp بر روی سرور نصب نیست")
        await state.clear()
        return
    
    # Validate platform
    url_lower = url.lower()
    if not any(x in url_lower for x in ["youtube.com", "youtu.be", "instagram.com", "twitter.com", "x.com", "tiktok.com"]):
        await message.reply(
            "❌ **پلتفرم پشتیبانی نشده**\n\n"
            "پلتفرم‌های پشتیبانی‌شده:\n"
            "• 🎥 YouTube\n"
            "• 📸 Instagram\n"
            "• 🐦 Twitter/X\n"
            "• 🎵 TikTok"
        )
        return
    
    # Store URL in session
    session_data = get_session(message.from_user.id)
    session_data["url"] = url
    
    # Move to STEP 2: Format type selection
    await state.set_state(DownloadStates.selecting_format_type)
    await message.answer(
        "🎯 **نوع فایل دریافتی را انتخاب کنید:**\n\n"
        "• 🎬 ویدیو - دانلود با کیفیت انتخابی\n"
        "• 🎵 صدا - فقط صدا را استخراج کنید",
        reply_markup=get_format_type_keyboard()
    )


# ==================== STEP 2: FORMAT TYPE SELECTION ====================

@router.callback_query(DownloadStates.selecting_format_type, F.data == "format_video")
async def select_video_format(query: CallbackQuery, state: FSMContext):
    """STEP 2A: Video format selected"""
    session_data = get_session(query.from_user.id)
    session_data["format_type"] = "video"
    
    await state.set_state(DownloadStates.video_quality_selection)
    await query.message.edit_text(
        "📺 **کیفیت ویدیو را انتخاب کنید:**\n\n"
        "━━━━ کیفیت بالا ━━━━\n"
        "• 🔵 4K (2160p) • ~2.1GB\n"
        "• 🟢 1080p • ~850MB\n\n"
        "━━━━ کیفیت متوسط ━━━━\n"
        "• 🟡 720p • ~420MB ✅ پیشنهاد\n"
        "• 🟠 480p • ~200MB\n\n"
        "━━━━ کیفیت پایین ━━━━\n"
        "• 🔴 360p • ~95MB\n"
        "• ⚫ 240p • ~45MB",
        reply_markup=get_video_quality_keyboard()
    )
    try:
        await query.answer()
    except Exception:
        pass


@router.callback_query(DownloadStates.selecting_format_type, F.data == "format_audio")
async def select_audio_format(query: CallbackQuery, state: FSMContext):
    """STEP 2B: Audio format selected"""
    session_data = get_session(query.from_user.id)
    session_data["format_type"] = "audio"
    
    await state.set_state(DownloadStates.audio_format_selection)
    await query.message.edit_text(
        "🎵 **فرمت صوتی را انتخاب کنید:**",
        reply_markup=get_audio_format_keyboard()
    )
    try:
        await query.answer()
    except Exception:
        pass


# ==================== STEP 3A: VIDEO QUALITY SELECTION ====================

@router.callback_query(DownloadStates.video_quality_selection, F.data.startswith("quality_"))
async def select_video_quality(query: CallbackQuery, state: FSMContext):
    """STEP 3A: Video quality selected"""
    quality_map = {
        "quality_4k": {"resolution": 2160, "format": "best[height<=2160]"},
        "quality_1080": {"resolution": 1080, "format": "best[height<=1080]"},
        "quality_720": {"resolution": 720, "format": "best[height<=720]"},
        "quality_480": {"resolution": 480, "format": "best[height<=480]"},
        "quality_360": {"resolution": 360, "format": "best[height<=360]"},
        "quality_240": {"resolution": 240, "format": "best[height<=240]"},
    }
    
    quality_data = quality_map.get(query.data)
    if not quality_data:
        await query.answer("❌ کیفیت نامعتبر", show_alert=True)
        return
    
    session_data = get_session(query.from_user.id)
    session_data["quality"] = quality_data
    
    await state.set_state(DownloadStates.video_codec_selection)
    await query.message.edit_text(
        "🎞️ **کدک ویدیو را انتخاب کنید:**\n\n"
        "• H.264 | MP4 ✅ سازگار با همه دستگاه‌ها\n"
        "• AV1 | WebM 🏆 بهترین کیفیت/حجم\n"
        "• VP9 | WebM ⚡ سبک و کارآمد\n\n"
        "<i>ℹ️ اگر مطمئن نیستید H.264 را انتخاب کنید</i>",
        reply_markup=get_video_codec_keyboard()
    )
    try:
        await query.answer()
    except Exception:
        pass


# ==================== STEP 4: VIDEO CODEC SELECTION ====================

@router.callback_query(DownloadStates.video_codec_selection, F.data.startswith("codec_"))
async def select_video_codec(query: CallbackQuery, state: FSMContext):
    """STEP 4: Video codec selected"""
    codec_map = {
        "codec_h264": {"name": "H.264", "format": "mp4"},
        "codec_av1": {"name": "AV1", "format": "webm"},
        "codec_vp9": {"name": "VP9", "format": "webm"},
    }
    
    codec_data = codec_map.get(query.data)
    if not codec_data:
        await query.answer("❌ کدک نامعتبر", show_alert=True)
        return
    
    session_data = get_session(query.from_user.id)
    session_data["codec"] = codec_data
    
    await state.set_state(DownloadStates.video_selecting_subtitle)
    await query.message.edit_text(
        "📝 **زیرنویس می‌خواهید؟**\n\n"
        "زیرنویس‌های موجود:\n"
        "• 🇮🇷 فارسی\n"
        "• 🇺🇸 English\n"
        "• 🇸🇦 عربی\n"
        "• 🇷🇺 Русский\n\n"
        "یا بدون زیرنویس",
        reply_markup=get_subtitle_keyboard()
    )
    try:
        await query.answer()
    except Exception:
        pass


# ==================== STEP 5: SUBTITLE SELECTION ====================

@router.callback_query(DownloadStates.video_selecting_subtitle, F.data.startswith("subtitle_"))
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
    
    session_data = get_session(query.from_user.id)
    session_data["subtitle"] = subtitle
    
    await state.set_state(DownloadStates.video_selecting_send_as)
    await query.message.edit_text(
        "📤 **نحوه دریافت فایل:**\n\n"
        "• 📹 ویدیو - قابل پخش در تلگرام\n"
        "• 📁 فایل - دانلود کامل",
        reply_markup=get_send_as_keyboard()
    )
    try:
        await query.answer()
    except Exception:
        pass


# ==================== STEP 6: SEND AS SELECTION ====================

@router.callback_query(DownloadStates.video_selecting_send_as, F.data.startswith("send_as_"))
async def select_send_as(query: CallbackQuery, state: FSMContext):
    """STEP 6: Send As selected"""
    send_as_map = {
        "send_as_video": "video",
        "send_as_file": "file",
    }
    
    send_as = send_as_map.get(query.data)
    if not send_as:
        await query.answer("❌ گزینه نامعتبر", show_alert=True)
        return
    
    session_data = get_session(query.from_user.id)
    session_data["send_as"] = send_as
    
    # Now start the download
    await state.set_state(DownloadStates.downloading)
    await start_download(query.message, query.from_user.id, state)


# ==================== STEP 3B: AUDIO FORMAT SELECTION ====================

@router.callback_query(DownloadStates.audio_format_selection, F.data.startswith("audio_"))
async def select_audio_format(query: CallbackQuery, state: FSMContext):
    """STEP 3B: Audio format selected"""
    audio_map = {
        "audio_mp3_320": {"format": "mp3", "bitrate": "320"},
        "audio_mp3_128": {"format": "mp3", "bitrate": "128"},
        "audio_aac_256": {"format": "aac", "bitrate": "256"},
        "audio_m4a_128": {"format": "m4a", "bitrate": "128"},
        "audio_opus": {"format": "opus", "bitrate": "128"},
    }
    
    audio_data = audio_map.get(query.data)
    if not audio_data:
        await query.answer("❌ فرمت نامعتبر", show_alert=True)
        return
    
    session_data = get_session(query.from_user.id)
    session_data["audio_format"] = audio_data
    
    # For audio, skip subtitle selection and go directly to download
    await state.set_state(DownloadStates.downloading)
    await start_download(query.message, query.from_user.id, state)


# ==================== STEP 7: ACTUAL DOWNLOAD ====================

async def start_download(message: Message, user_id: int, state: FSMContext):
    """STEP 7: Start actual download"""
    session_data = get_session(user_id)
    url = session_data.get("url")
    format_type = session_data.get("format_type")
    
    if not url:
        await message.answer("❌ خطا: URL پیدا نشد")
        clear_session(user_id)
        await state.clear()
        return
    
    # Show downloading progress message
    progress_msg = await message.answer(
        generate_progress_message(
            title="جاری سازی دانلود...",
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
        # Create temp directory
        temp_dir = Path("temp_downloads")
        temp_dir.mkdir(exist_ok=True)
        
        # Build yt-dlp options based on selection
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'outtmpl': str(temp_dir / '%(title)s.%(ext)s'),
        }
        
        if format_type == "video":
            quality_data = session_data.get("quality", {})
            codec_data = session_data.get("codec", {})
            
            # Set format based on codec
            if codec_data.get("name") == "H.264":
                ydl_opts['format'] = 'best[ext=mp4][vcodec^=h264]'
            elif codec_data.get("name") == "AV1":
                ydl_opts['format'] = 'best[ext=webm][vcodec^=av1]'
            elif codec_data.get("name") == "VP9":
                ydl_opts['format'] = 'best[ext=webm][vcodec^=vp9]'
            else:
                ydl_opts['format'] = 'best[ext=mp4]'
            
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'prefixFields': '-',
                'args': ['-c:v', 'copy', '-c:a', 'aac'],
            }]
        else:  # audio
            audio_fmt = session_data.get("audio_format", {})
            format_name = audio_fmt.get("format", "mp3")
            
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format_name,
                'preferredquality': audio_fmt.get("bitrate", "128"),
            }]
        
        # Download with yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        # Get file size
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            file_size_mb = file_size / (1024 * 1024)
            final_filename = filename

            # --- Adaptive Compression ---
            # If video is larger than 20MB, try to compress it
            if format_type == "video" and file_size_mb > 20:
                try:
                    await progress_msg.edit_text(
                        "⚙️ در حال فشرده‌سازی هوشمند...\nاین عملیات ممکن است چند دقیقه طول بکشد.",
                        parse_mode="HTML"
                    )
                    from services.compression_service import AdaptiveCompression
                    adaptive = AdaptiveCompression()
                    compressed_path = filename.rsplit(".", 1)[0] + "_compressed.mp4"
                    result = await adaptive.auto_compress(
                        file_path=filename,
                        output_path=compressed_path,
                        target_size_mb=48,  # Keep under Telegram limit
                        device_type="mobile",
                        connection="4g"
                    )
                    if result.get("status") == "success" and os.path.exists(compressed_path):
                        os.remove(filename)
                        final_filename = compressed_path
                        file_size = os.path.getsize(final_filename)
                        file_size_mb = file_size / (1024 * 1024)
                except Exception as compress_err:
                    # Compression failed, continue with original file
                    pass

            # Check Telegram file size limit
            if file_size > 50 * 1024 * 1024:
                await progress_msg.delete()
                await message.answer(
                    f"❌ **فایل بیش از حد بزرگ است**\n\n"
                    f"اندازه: {file_size_mb:.1f} MB\n"
                    f"حد مجاز: 50 MB"
                )
                try:
                    os.remove(final_filename)
                except Exception:
                    pass
            else:
                # Send the file using FSInputFile
                send_as = session_data.get("send_as", "file")
                caption = (
                    f"✅ **دانلود موفق!**\n\n"
                    f"📹 {info.get('title', 'Media')}\n"
                    f"💾 {file_size_mb:.1f} MB"
                )
                
                try:
                    if send_as == "video" and format_type == "video":
                        await message.reply_video(
                            FSInputFile(final_filename),
                            caption=caption
                        )
                    else:
                        await message.reply_document(
                            FSInputFile(final_filename),
                            caption=caption
                        )
                except Exception as e:
                    await message.answer(f"❌ خطا در ارسال: {str(e)[:50]}")
                
                # Delete progress message
                try:
                    await progress_msg.delete()
                except Exception:
                    pass
                
                # Cleanup temp file
                try:
                    os.remove(final_filename)
                except Exception:
                    pass
        else:
            await message.answer("❌ فایل دانلود شده پیدا نشد")
    
    except Exception as e:
        try:
            await progress_msg.delete()
        except Exception:
            pass
        
        await message.answer(safe_user_message(e, context=f"download url={url}"))
    
    finally:
        # Cleanup
        clear_session(user_id)
        await state.clear()


# ==================== BACK BUTTONS ====================

@router.callback_query(F.data == "cancel_download")
async def cancel_download(query: CallbackQuery, state: FSMContext):
    """Cancel download and go back"""
    clear_session(query.from_user.id)
    await state.clear()
    await query.message.delete()
    await query.answer("❌ دانلود لغو شد", show_alert=False)


@router.callback_query(F.data == "back_to_format")
async def back_to_format(query: CallbackQuery, state: FSMContext):
    """Go back to format type selection"""
    await state.set_state(DownloadStates.selecting_format_type)
    await query.message.edit_text(
        "🎯 **نوع فایل دریافتی را انتخاب کنید:**",
        reply_markup=get_format_type_keyboard()
    )
    try:
        await query.answer()
    except Exception:
        pass


@router.callback_query(F.data == "back_to_quality")
async def back_to_quality(query: CallbackQuery, state: FSMContext):
    """Go back to quality selection"""
    await state.set_state(DownloadStates.video_quality_selection)
    await query.message.edit_text(
        "📺 **کیفیت ویدیو را انتخاب کنید:**",
        reply_markup=get_video_quality_keyboard()
    )
    try:
        await query.answer()
    except Exception:
        pass


@router.callback_query(F.data == "back_to_codec")
async def back_to_codec(query: CallbackQuery, state: FSMContext):
    """Go back to codec selection"""
    await state.set_state(DownloadStates.video_codec_selection)
    await query.message.edit_text(
        "🎞️ **کدک ویدیو را انتخاب کنید:**",
        reply_markup=get_video_codec_keyboard()
    )
    try:
        await query.answer()
    except Exception:
        pass


@router.callback_query(F.data == "back_to_subtitle")
async def back_to_subtitle(query: CallbackQuery, state: FSMContext):
    """Go back to subtitle selection"""
    await state.set_state(DownloadStates.video_selecting_subtitle)
    await query.message.edit_text(
        "📝 **زیرنویس می‌خواهید؟**",
        reply_markup=get_subtitle_keyboard()
    )
    try:
        await query.answer()
    except Exception:
        pass


__all__ = ["router"]
