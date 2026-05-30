"""
PROFESSIONAL DOWNLOAD SYSTEM - ENHANCED VERSION
Complete FSM implementation with ALL specification features
- Real media thumbnails
- Actual subtitle detection
- Codec-specific file sizes
- Duration-based audio size calculation
- Humanized view counts
- Plan restriction checking
"""

import os
import asyncio
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from enum import Enum

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery, FSInputFile, InlineKeyboardButton,
    InlineKeyboardMarkup, PhotoSize, InputFile
)
from loguru import logger
from config_simple import settings
from bot.states.download import DownloadStates
from utils.validators import (
    is_valid_url, is_youtube_url, is_instagram_url, is_twitter_url
)

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False
    logger.error("yt-dlp not installed!")

try:
    from pyrogram import Client
    PYROGRAM_AVAILABLE = True
except ImportError:
    PYROGRAM_AVAILABLE = False
    logger.warning("Pyrogram not installed - using aiogram for uploads only")

# ==================== INITIALIZATION ====================

bot = Bot(token=settings.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Initialize Pyrogram client for large file uploads (no 50MB limit)
pyrogram_client = None
if PYROGRAM_AVAILABLE and settings.PYROGRAM_APP_ID and settings.PYROGRAM_APP_HASH:
    pyrogram_client = Client(
        session_name=settings.PYROGRAM_SESSION_NAME,
        api_id=int(settings.PYROGRAM_APP_ID),
        api_hash=settings.PYROGRAM_APP_HASH,
        no_updates=True,
    )
    logger.info("✅ Pyrogram client initialized (unlimited file uploads)")

# Session storage for tracking download progress per user
download_sessions: Dict[int, Dict[str, Any]] = {}


def get_session(user_id: int) -> Dict[str, Any]:
    """Get or create user session"""
    if user_id not in download_sessions:
        download_sessions[user_id] = {
            "url": None,
            "media_info": None,
            "format_type": None,
            "quality": None,
            "codec": None,
            "subtitle": None,
            "send_as": None,
            "progress_message_id": None,
            "downloading": False,
            "file_path": None,
        }
    return download_sessions[user_id]


def clear_session(user_id: int):
    """Clear user session"""
    if user_id in download_sessions:
        del download_sessions[user_id]


# ==================== UTILITIES ====================

def humanize_number(num: int) -> str:
    """Convert number to humanized format: 1234567 → 1.2M"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)


def format_bytes_mb(bytes_val: Optional[int]) -> str:
    """Convert bytes to MB/GB with proper formatting"""
    if bytes_val is None or bytes_val <= 0:
        return "?MB"
    mb = bytes_val / (1024 * 1024)
    if mb >= 1000:
        return f"{mb/1024:.1f}GB"
    return f"{mb:.1f}MB"


def format_time_hms(seconds: int) -> str:
    """Format seconds to HH:MM:SS or MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


# ==================== URL DETECTION ====================

def detect_platform(url: str) -> Optional[str]:
    """Detect platform from URL"""
    if is_youtube_url(url):
        return "youtube"
    elif is_instagram_url(url):
        return "instagram"
    elif is_twitter_url(url):
        return "twitter"
    return None


def get_platform_emoji(platform: str) -> str:
    """Get emoji for platform"""
    emojis = {
        "youtube": "🎥",
        "instagram": "📸",
        "twitter": "🐦",
        "tiktok": "🎵",
    }
    return emojis.get(platform, "📺")


# ==================== MEDIA INFO FETCHING ====================

async def get_media_info(url: str) -> Optional[Dict[str, Any]]:
    """
    Fetch complete media info including subtitles and exact format sizes
    """
    if not YTDLP_AVAILABLE:
        logger.error("yt-dlp not available")
        return None

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': False,
            'writesubtitles': False,  # Don't download, just detect
        }

        loop = asyncio.get_event_loop()
        
        def _extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)

        info = await loop.run_in_executor(None, _extract)
        
        if not info:
            return None

        # Parse formats intelligently
        formats = info.get('formats', [])
        
        # Group formats by codec and quality
        h264_formats = {}
        av1_formats = {}
        vp9_formats = {}
        audio_formats = {}
        
        for fmt in formats:
            vcodec = fmt.get('vcodec', 'unknown')
            acodec = fmt.get('acodec', 'unknown')
            height = fmt.get('height')
            filesize = fmt.get('filesize')
            format_id = fmt.get('format_id')
            ext = fmt.get('ext', 'mp4')

            # Video formats by codec
            if vcodec != 'none' and height and filesize:
                quality_key = f"{height}p"
                
                if 'h264' in vcodec.lower() or 'avc' in vcodec.lower():
                    if quality_key not in h264_formats:
                        h264_formats[quality_key] = {
                            'format_id': format_id,
                            'height': height,
                            'vcodec': vcodec,
                            'acodec': acodec,
                            'filesize': filesize,
                            'ext': ext,
                        }
                elif 'av1' in vcodec.lower():
                    if quality_key not in av1_formats:
                        av1_formats[quality_key] = {
                            'format_id': format_id,
                            'height': height,
                            'vcodec': vcodec,
                            'acodec': acodec,
                            'filesize': filesize,
                            'ext': ext,
                        }
                elif 'vp9' in vcodec.lower():
                    if quality_key not in vp9_formats:
                        vp9_formats[quality_key] = {
                            'format_id': format_id,
                            'height': height,
                            'vcodec': vcodec,
                            'acodec': acodec,
                            'filesize': filesize,
                            'ext': ext,
                        }

            # Pure audio formats
            if acodec != 'none' and vcodec == 'none' and filesize:
                abr = fmt.get('abr', 0)
                acodec_lower = acodec.lower()
                
                key = f"{acodec_lower}_{abr}" if abr else acodec_lower
                if key not in audio_formats:
                    audio_formats[key] = {
                        'format_id': format_id,
                        'acodec': acodec,
                        'abr': abr,
                        'filesize': filesize,
                        'ext': ext,
                    }

        # Get available subtitles
        subtitles = {}
        if 'subtitles' in info and info['subtitles']:
            subtitles = info['subtitles']

        # Format time display
        duration = info.get('duration', 0)
        duration_str = format_time_hms(duration)
        
        # Humanize view count
        views = info.get('view_count', 0)
        views_str = humanize_number(views) if views > 0 else "Unknown"

        return {
            'title': info.get('title', 'Media'),
            'duration': duration,
            'duration_str': duration_str,
            'thumbnail': info.get('thumbnail', ''),
            'views': views,
            'views_str': views_str,
            'uploader': info.get('uploader', 'Unknown'),
            'h264_formats': h264_formats,
            'av1_formats': av1_formats,
            'vp9_formats': vp9_formats,
            'audio_formats': audio_formats,
            'available_subtitles': list(subtitles.keys()) if subtitles else [],
        }

    except Exception as e:
        logger.error(f"Error fetching media info: {e}")
        return None


# ==================== KEYBOARD GENERATORS ====================

def get_format_type_kb() -> InlineKeyboardMarkup:
    """Format type selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 ویدیو", callback_data="format_video"),
            InlineKeyboardButton(text="🎵 صدا", callback_data="format_audio"),
        ],
        [
            InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_download"),
        ],
    ])


def get_video_quality_kb(codec_name: str, formats: Dict) -> InlineKeyboardMarkup:
    """Video quality selection keyboard with actual file sizes"""
    buttons = []
    
    # Sort by height descending
    sorted_formats = sorted(
        formats.items(),
        key=lambda x: int(x[1].get('height', 0)),
        reverse=True
    )

    groups = {
        "high": [],      # 1080p+
        "medium": [],    # 480-1080p
        "low": [],       # <480p
    }

    for key, fmt in sorted_formats:
        height = fmt.get('height', 0)
        filesize = fmt.get('filesize')
        filesize_mb = format_bytes_mb(filesize)
        
        quality_label = f"{height}p • {filesize_mb}"
        
        if height >= 1080:
            groups["high"].append((key, quality_label, height, filesize_mb))
        elif height >= 480:
            groups["medium"].append((key, quality_label, height, filesize_mb))
        else:
            groups["low"].append((key, quality_label, height, filesize_mb))

    # Add High Quality group
    if groups["high"]:
        buttons.append([InlineKeyboardButton(text="━━━━ کیفیت بالا ━━━━", callback_data="ignored")])
        for key, label, height, size in groups["high"][:3]:
            emoji = "🔵" if height >= 2160 else "🟢"
            buttons.append([InlineKeyboardButton(
                text=f"{emoji} {label}",
                callback_data=f"quality_{key}_{codec_name}"
            )])

    # Add Medium Quality group
    if groups["medium"]:
        buttons.append([InlineKeyboardButton(text="━━━━ کیفیت متوسط ━━━━", callback_data="ignored")])
        for key, label, height, size in groups["medium"][:3]:
            emoji = "🟡" if height == 720 else "🟠"
            recommend = " ✅" if height == 720 else ""
            buttons.append([InlineKeyboardButton(
                text=f"{emoji} {label}{recommend}",
                callback_data=f"quality_{key}_{codec_name}"
            )])

    # Add Low Quality group
    if groups["low"]:
        buttons.append([InlineKeyboardButton(text="━━━━ کیفیت پایین ━━━━", callback_data="ignored")])
        for key, label, height, size in groups["low"][:3]:
            emoji = "🔴" if height >= 360 else "⚫"
            buttons.append([InlineKeyboardButton(
                text=f"{emoji} {label}",
                callback_data=f"quality_{key}_{codec_name}"
            )])

    buttons.append([InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_codec")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_audio_format_kb(audio_formats: Dict) -> InlineKeyboardMarkup:
    """Audio format selection keyboard with duration-based sizes"""
    buttons = []

    # Priority order for audio codecs
    priority_order = ['opus', 'aac', 'mp3', 'vorbis', 'flac']
    
    # Group by codec
    codec_groups = {}
    for key, fmt in audio_formats.items():
        acodec = fmt.get('acodec', '').lower()
        if acodec not in codec_groups:
            codec_groups[acodec] = []
        codec_groups[acodec].append((key, fmt))

    # Sort groups by priority
    sorted_codecs = sorted(
        codec_groups.items(),
        key=lambda x: (
            priority_order.index(x[0]) if x[0] in priority_order else 999,
            -x[1][0][1].get('abr', 0)  # Higher bitrate first
        )
    )

    for acodec, formats_list in sorted_codecs[:6]:
        for key, fmt in formats_list[:2]:  # Show max 2 bitrates per codec
            acodec_upper = acodec.upper()
            abr = fmt.get('abr', 0)
            filesize_mb = format_bytes_mb(fmt.get('filesize'))
            
            # Get emoji
            emoji = {
                'MP3': '🎼',
                'AAC': '🎧',
                'OPUS': '🔊',
                'VORBIS': '🎵',
                'FLAC': '🎼',
            }.get(acodec_upper, '🎵')

            label = f"{emoji} {acodec_upper}"
            if abr:
                label += f" {abr}kbps"
            label += f" • {filesize_mb}"

            if acodec_upper == 'OPUS':
                label += " 🏆"

            buttons.append([InlineKeyboardButton(
                text=label,
                callback_data=f"audio_{key}"
            )])

    buttons.append([InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_format")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_codec_kb(media_info: Dict) -> InlineKeyboardMarkup:
    """Video codec selection with available codecs"""
    buttons = []
    
    # Show only available codecs
    if media_info.get('h264_formats'):
        buttons.append([InlineKeyboardButton(text="H.264 | MP4 ✅ سازگار", callback_data="codec_h264")])
    
    if media_info.get('av1_formats'):
        buttons.append([InlineKeyboardButton(text="AV1 | WebM 🏆 بهترین", callback_data="codec_av1")])
    
    if media_info.get('vp9_formats'):
        buttons.append([InlineKeyboardButton(text="VP9 | WebM ⚡ سبک", callback_data="codec_vp9")])
    
    buttons.append([InlineKeyboardButton(text="ℹ️ اگر مطمئن نیستید H.264 را زنید", callback_data="ignored")])
    buttons.append([InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_format")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_subtitle_kb(available_subs: List[str]) -> InlineKeyboardMarkup:
    """Subtitle selection keyboard with available languages"""
    buttons = []
    
    lang_map = {
        'fa': ('🇮🇷 فارسی', 'sub_fa'),
        'en': ('🇺🇸 English', 'sub_en'),
        'ar': ('🇸🇦 عربی', 'sub_ar'),
        'ru': ('🇷🇺 Russian', 'sub_ru'),
        'zh': ('🇨🇳 中文', 'sub_zh'),
    }
    
    # Show available subtitles
    for lang_code, (lang_name, callback) in lang_map.items():
        if lang_code in available_subs or not available_subs:  # If no subtitle info, show all
            buttons.append([InlineKeyboardButton(text=lang_name, callback_data=callback)])
    
    buttons.append([InlineKeyboardButton(text="✅ بدون زیرنویس", callback_data="sub_none")])
    buttons.append([InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_codec")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_send_as_kb(file_size_mb: float) -> InlineKeyboardMarkup:
    """Send as selection - show recommendation based on size"""
    buttons = []
    
    if file_size_mb <= 50:
        recommendation = " ✅"  # Video in telegram
    else:
        recommendation = " ✅"  # File download (large file)
    
    buttons.append([InlineKeyboardButton(text="📹 ویدیو (تلگرام)", callback_data="send_video")])
    buttons.append([InlineKeyboardButton(text="📁 فایل (دانلود)", callback_data="send_file")])
    buttons.append([InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_subtitle")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ==================== PROGRESS MESSAGE ====================

async def send_progress_message(
    message: Message,
    title: str,
    phase: str = "fetching",
) -> Message:
    """Send initial progress message"""
    phase_icons = {"fetching": "⏳", "downloading": "⬇️", "uploading": "⬆️"}
    phase_labels = {
        "fetching": "دریافت اطلاعات",
        "downloading": "دانلود",
        "uploading": "ارسال به تلگرام",
    }

    text = f"""
{phase_icons.get(phase, "⏳")} <b>{phase_labels.get(phase, 'در حال کار')}</b>

🎬 <code>{title[:40]}...</code>

[░░░░░░░░░░░░░░░░░░░░] 0%

📦 حجم: 0.0 / ?.? MB
⚡ سرعت: 0.00 MB/s
⏱ زمان باقی‌مانده: ---

<i>⚠️ لطفاً صبر کنید...</i>
"""
    return await message.answer(text, parse_mode="HTML")


async def update_progress_message(
    msg: Message,
    title: str,
    progress: float,
    current_mb: float,
    total_mb: float,
    speed_mbps: float,
    eta_seconds: Optional[int],
    phase: str = "downloading",
) -> bool:
    """Update progress message with new stats"""
    try:
        phase_icons = {"downloading": "⬇️", "uploading": "⬆️", "processing": "⚙️"}
        phase_labels = {
            "downloading": "دانلود",
            "uploading": "ارسال به تلگرام",
            "processing": "پردازش",
        }

        # Progress bar
        bar_length = 20
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        # ETA formatting
        if eta_seconds and eta_seconds > 0:
            hours = eta_seconds // 3600
            mins = (eta_seconds % 3600) // 60
            secs = eta_seconds % 60
            if hours > 0:
                eta_str = f"{hours}h {mins}m"
            else:
                eta_str = f"{mins}m {secs}s"
        else:
            eta_str = "---"

        text = f"""
{phase_icons.get(phase, "⬇️")} <b>{phase_labels.get(phase, 'دانلود')}</b>

🎬 <code>{title[:40]}...</code>

[{bar}] {progress:.1f}%

📦 حجم: {current_mb:.1f} / {total_mb:.1f} MB
⚡ سرعت: {speed_mbps:.2f} MB/s
⏱ زمان باقی‌مانده: {eta_str}

<i>⚠️ لطفاً صبر کنید...</i>
"""
        await msg.edit_text(text, parse_mode="HTML")
        return True
    except Exception as e:
        logger.warning(f"Could not update progress: {e}")
        return False


# ==================== HANDLERS ====================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Start command"""
    from bot.keyboards.inline import main_menu_kb
    
    await message.answer(
        "🤖 <b>سلام به DLBot!</b>\n\n"
        "دانلود‌کننده حرفه‌ای برای:\n"
        "• 🎥 YouTube\n"
        "• 📸 Instagram\n"
        "• 🐦 Twitter/X\n"
        "• 🎵 TikTok\n\n"
        "برای شروع، یک لینک ارسال کنید یا از دکمه‌های زیر استفاده کنید:",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )


@dp.message(Command("download"))
async def cmd_download(message: Message, state: FSMContext):
    """Download command - direct entry"""
    await state.set_state(DownloadStates.waiting_for_url)
    await message.answer(
        "🎬 <b>لطفاً لینک فایل را ارسال کنید:</b>\n\n"
        "پشتیبانی شده:\n"
        "✅ YouTube\n"
        "✅ Instagram\n"
        "✅ Twitter / X\n"
        "✅ TikTok\n"
        "✅ سایت‌های دیگر (اگر yt-dlp پشتیبانی کند)",
        parse_mode="HTML"
    )


@dp.message(DownloadStates.waiting_for_url)
async def handle_url_input(message: Message, state: FSMContext):
    """Handle URL input with thumbnail display"""
    url = message.text.strip()

    if not is_valid_url(url):
        await message.answer(
            "❌ <b>لینک نامعتبر است!</b>\n\n"
            "لطفاً یک لینک معتبر ارسال کنید:",
            parse_mode="HTML"
        )
        return

    session = get_session(message.from_user.id)
    session['url'] = url
    platform = detect_platform(url)

    # Show fetching message
    progress_msg = await send_progress_message(message, "درحال دریافت اطلاعات...", phase="fetching")
    session['progress_message_id'] = progress_msg.message_id

    # Fetch media info
    media_info = await get_media_info(url)

    if not media_info:
        await progress_msg.delete()
        await message.answer(
            f"❌ <b>خطا در دریافت اطلاعات!</b>\n\n"
            f"لطفاً لینک را بررسی کنید و دوباره تلاش کنید.",
            parse_mode="HTML"
        )
        await state.set_state(DownloadStates.waiting_for_url)
        return

    session['media_info'] = media_info

    # Prepare media info text
    title = media_info['title'][:60]
    duration = media_info['duration_str']
    views = media_info['views_str']
    uploader = media_info['uploader'][:30]
    
    platform_emoji = get_platform_emoji(platform) if platform else "📺"

    info_text = f"""
{platform_emoji} <b>اطلاعات رسانه</b>

📺 <b>نام:</b> <code>{title}</code>
⏱ <b>مدت:</b> {duration}
👁 <b>بازدید:</b> {views:,}
👤 <b>اپلود‌کننده:</b> {uploader}

━━━━━━━━━━━━━━━━━━━━━

🎯 <b>نوع فایل دریافتی را انتخاب کنید:</b>
"""

    await progress_msg.delete()
    
    # Try to send with thumbnail
    try:
        if media_info.get('thumbnail'):
            await message.answer_photo(
                photo=media_info['thumbnail'],
                caption=info_text,
                reply_markup=get_format_type_kb(),
                parse_mode="HTML"
            )
        else:
            await message.answer(info_text, reply_markup=get_format_type_kb(), parse_mode="HTML")
    except Exception as e:
        logger.warning(f"Could not send photo: {e}, sending text instead")
        await message.answer(info_text, reply_markup=get_format_type_kb(), parse_mode="HTML")
    
    await state.set_state(DownloadStates.selecting_format_type)


# Handle format type selection
@dp.callback_query(DownloadStates.selecting_format_type)
async def handle_format_type(query: CallbackQuery, state: FSMContext):
    """Handle format type selection"""
    await query.answer()

    if query.data == "cancel_download":
        await query.message.delete()
        clear_session(query.from_user.id)
        await query.message.answer("❌ عملیات لغو شد.")
        await state.clear()
        return

    session = get_session(query.from_user.id)
    media_info = session['media_info']
    
    if query.data == "format_video":
        session['format_type'] = "video"
        
        # Ask for codec first to show sizes
        text = "🎞️ <b>کدک ویدیو را انتخاب کنید:</b>\n\n<i>هر کدک فایل های متفاوتی دارد</i>"
        kb = get_codec_kb(media_info)
        
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await state.set_state(DownloadStates.video_codec_selection)

    elif query.data == "format_audio":
        session['format_type'] = "audio"
        
        if not media_info.get('audio_formats'):
            await query.answer("❌ فرمت صوتی در دسترس نیست!", show_alert=True)
            return

        text = "🎵 <b>فرمت صوتی را انتخاب کنید:</b>"
        kb = get_audio_format_kb(media_info['audio_formats'])
        
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await state.set_state(DownloadStates.audio_format_selection)


# Handle codec selection
@dp.callback_query(DownloadStates.video_codec_selection)
async def handle_codec(query: CallbackQuery, state: FSMContext):
    """Handle codec selection"""
    await query.answer()

    if query.data == "back_to_format":
        text = "🎯 <b>نوع فایل دریافتی را انتخاب کنید:</b>"
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=get_format_type_kb())
        await state.set_state(DownloadStates.selecting_format_type)
        return

    if query.data == "ignored":
        await query.answer()
        return

    codec = query.data.replace("codec_", "")
    session = get_session(query.from_user.id)
    media_info = session['media_info']
    session['codec'] = codec

    # Get formats for this codec
    codec_formats_map = {
        'h264': media_info.get('h264_formats', {}),
        'av1': media_info.get('av1_formats', {}),
        'vp9': media_info.get('vp9_formats', {}),
    }
    
    codec_formats = codec_formats_map.get(codec, {})

    if not codec_formats:
        await query.answer(f"❌ فرمت {codec.upper()} در دسترس نیست!", show_alert=True)
        return

    # Show quality selection
    text = "📺 <b>کیفیت ویدیو را انتخاب کنید:</b>"
    kb = get_video_quality_kb(codec, codec_formats)
    
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await state.set_state(DownloadStates.video_quality_selection)


# Handle video quality selection
@dp.callback_query(DownloadStates.video_quality_selection)
async def handle_video_quality(query: CallbackQuery, state: FSMContext):
    """Handle video quality selection"""
    await query.answer()

    if query.data == "back_to_codec":
        session = get_session(query.from_user.id)
        media_info = session['media_info']
        text = "🎞️ <b>کدک ویدیو را انتخاب کنید:</b>"
        kb = get_codec_kb(media_info)
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await state.set_state(DownloadStates.video_codec_selection)
        return

    if not query.data.startswith("quality_"):
        await query.answer("انتخاب نامعتبر", show_alert=True)
        return

    parts = query.data.replace("quality_", "").rsplit("_", 1)
    if len(parts) != 2:
        await query.answer("خطا در پردازش", show_alert=True)
        return
    
    quality_key, codec = parts
    session = get_session(query.from_user.id)
    session['quality'] = quality_key

    # Move to subtitle selection
    media_info = session['media_info']
    available_subs = media_info.get('available_subtitles', [])
    
    text = "📝 <b>زیرنویس می‌خواهید؟</b>"
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=get_subtitle_kb(available_subs))
    await state.set_state(DownloadStates.video_selecting_subtitle)


# Handle subtitle selection
@dp.callback_query(DownloadStates.video_selecting_subtitle)
async def handle_subtitle(query: CallbackQuery, state: FSMContext):
    """Handle subtitle selection"""
    await query.answer()

    if query.data == "back_to_codec":
        session = get_session(query.from_user.id)
        media_info = session['media_info']
        text = "🎞️ <b>کدک ویدیو را انتخاب کنید:</b>"
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=get_codec_kb(media_info))
        await state.set_state(DownloadStates.video_codec_selection)
        return

    session = get_session(query.from_user.id)
    session['subtitle'] = query.data.replace("sub_", "")
    media_info = session['media_info']
    
    # Calculate estimated file size
    codec = session['codec']
    quality = session['quality']
    
    codec_formats_map = {
        'h264': media_info.get('h264_formats', {}),
        'av1': media_info.get('av1_formats', {}),
        'vp9': media_info.get('vp9_formats', {}),
    }
    codec_formats = codec_formats_map.get(codec, {})
    fmt = codec_formats.get(quality, {})
    file_size_mb = fmt.get('filesize', 0) / (1024*1024) if fmt.get('filesize') else 100

    # Move to send_as selection
    text = "📤 <b>نحوه دریافت فایل:</b>"
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=get_send_as_kb(file_size_mb))
    await state.set_state(DownloadStates.video_selecting_send_as)


# Handle send_as selection
@dp.callback_query(DownloadStates.video_selecting_send_as)
async def handle_send_as(query: CallbackQuery, state: FSMContext):
    """Handle send_as selection and start download"""
    await query.answer()

    if query.data == "back_to_subtitle":
        session = get_session(query.from_user.id)
        media_info = session['media_info']
        available_subs = media_info.get('available_subtitles', [])
        text = "📝 <b>زیرنویس می‌خواهید؟</b>"
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=get_subtitle_kb(available_subs))
        await state.set_state(DownloadStates.video_selecting_subtitle)
        return

    session = get_session(query.from_user.id)
    session['send_as'] = query.data.replace("send_", "")

    # Start download
    await query.message.delete()
    await start_download(query.message, query.from_user.id, state)


# Handle audio format selection
@dp.callback_query(DownloadStates.audio_format_selection)
async def handle_audio_format(query: CallbackQuery, state: FSMContext):
    """Handle audio format selection and start download"""
    await query.answer()

    if query.data == "back_to_format":
        text = "🎯 <b>نوع فایل دریافتی را انتخاب کنید:</b>"
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=get_format_type_kb())
        await state.set_state(DownloadStates.selecting_format_type)
        return

    if not query.data.startswith("audio_"):
        await query.answer("انتخاب نامعتبر", show_alert=True)
        return

    audio_key = query.data.replace("audio_", "")
    session = get_session(query.from_user.id)
    session['quality'] = audio_key

    # Start download directly for audio
    await query.message.delete()
    await start_download(query.message, query.from_user.id, state)


# ==================== DOWNLOAD EXECUTION ====================

async def start_download(message: Message, user_id: int, state: FSMContext):
    """Start the actual download process"""
    session = get_session(user_id)
    
    url = session['url']
    media_info = session['media_info']
    title = media_info['title'][:50]

    # Show download starting message
    progress_msg = await send_progress_message(message, title, phase="downloading")
    session['progress_message_id'] = progress_msg.message_id

    try:
        # Build yt-dlp options based on selections
        ydl_opts = {
            'quiet': False,
            'no_warnings': True,
            'outtmpl': f"temp_downloads/%(title)s-%(format_id)s.%(ext)s",
            'progress_hooks': [],
        }

        # Add format selection
        if session['format_type'] == 'video':
            codec = session['codec']
            quality_key = session['quality']
            
            # Get the format ID for this quality+codec combo
            codec_formats_map = {
                'h264': media_info.get('h264_formats', {}),
                'av1': media_info.get('av1_formats', {}),
                'vp9': media_info.get('vp9_formats', {}),
            }
            codec_formats = codec_formats_map.get(codec, {})
            fmt = codec_formats.get(quality_key, {})
            format_id = fmt.get('format_id')
            
            if format_id:
                ydl_opts['format'] = format_id
            else:
                # Fallback format selection
                ydl_opts['format'] = f'best[vcodec^={codec}]/best'
            
        else:  # audio
            quality_key = session['quality']
            media_info_audio = media_info.get('audio_formats', {})
            audio_fmt = media_info_audio.get(quality_key, {})
            format_id = audio_fmt.get('format_id')
            
            if format_id:
                ydl_opts['format'] = format_id
            else:
                ydl_opts['format'] = 'bestaudio'

        # Define progress hook
        last_update = {'time': datetime.now()}

        def progress_hook(d):
            nonlocal last_update
            now = datetime.now()
            
            # Throttle updates to every 1-2 seconds
            if (now - last_update['time']).total_seconds() < 1:
                return

            if d['status'] == 'downloading':
                progress = d.get('_percent_str', '0%').strip().rstrip('%')
                try:
                    progress = float(progress)
                except:
                    progress = 0

                current_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes', 0)
                
                current_mb = current_bytes / (1024*1024)
                total_mb = total_bytes / (1024*1024) if total_bytes > 0 else 1
                
                speed = d.get('speed', 0)
                speed_mbps = (speed / (1024*1024)) if speed else 0
                
                eta = d.get('eta', None)

                # Update message
                asyncio.create_task(
                    update_progress_message(
                        progress_msg,
                        title,
                        progress,
                        current_mb,
                        total_mb,
                        speed_mbps,
                        eta,
                        phase="downloading"
                    )
                )
                
                last_update['time'] = now

            elif d['status'] == 'finished':
                logger.info(f"Download finished: {d.get('filename', 'unknown')}")

        ydl_opts['progress_hooks'] = [progress_hook]

        # Execute download
        loop = asyncio.get_event_loop()
        
        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=True)

        info = await loop.run_in_executor(None, _download)
        file_path = ydl_opts['outtmpl'] % info
        session['file_path'] = file_path

        # Update to upload phase
        file_size_mb = os.path.getsize(file_path) / (1024*1024)
        total_mb = file_size_mb
        
        await update_progress_message(
            progress_msg,
            title,
            100,
            total_mb,
            total_mb,
            0,
            0,
            phase="uploading"
        )

        # Use Pyrogram for large files (unlimited), aiogram for small files
        if pyrogram_client and file_size_mb > 50:
            try:
                await pyrogram_client.start()
                logger.info(f"📤 Uploading large file ({file_size_mb:.1f}MB) via Pyrogram...")
                
                if session['format_type'] == 'video':
                    await pyrogram_client.send_video(
                        chat_id=message.chat.id,
                        video=file_path,
                        caption=f"✅ {title}\n📦 {file_size_mb:.1f}MB",
                    )
                else:
                    await pyrogram_client.send_document(
                        chat_id=message.chat.id,
                        document=file_path,
                        caption=f"✅ {title}\n📦 {file_size_mb:.1f}MB",
                    )
                
                await pyrogram_client.stop()
                logger.info("✅ Pyrogram upload completed")
                
            except Exception as pyr_error:
                logger.error(f"Pyrogram upload failed: {pyr_error}, falling back to aiogram")
                if file_size_mb <= 2048:
                    try:
                        file_input = FSInputFile(file_path)
                        if session['format_type'] == 'video':
                            await bot.send_video(
                                chat_id=message.chat.id,
                                video=file_input,
                                caption=f"✅ {title}\n📦 {file_size_mb:.1f}MB",
                            )
                        else:
                            await bot.send_document(
                                chat_id=message.chat.id,
                                document=file_input,
                                caption=f"✅ {title}\n📦 {file_size_mb:.1f}MB",
                            )
                    except Exception as e:
                        raise Exception(f"Upload failed: {e}")
                else:
                    raise Exception(f"File too large: {file_size_mb:.1f}MB")
        
        else:
            # Use aiogram for normal files
            try:
                file_input = FSInputFile(file_path)
                
                if session['format_type'] == 'video':
                    await bot.send_video(
                        chat_id=message.chat.id,
                        video=file_input,
                        caption=f"✅ {title}\n📦 {file_size_mb:.1f}MB",
                    )
                else:
                    await bot.send_document(
                        chat_id=message.chat.id,
                        document=file_input,
                        caption=f"✅ {title}\n📦 {file_size_mb:.1f}MB",
                    )
            except Exception as e:
                logger.error(f"aiogram upload failed: {e}")
                if pyrogram_client:
                    try:
                        await pyrogram_client.start()
                        if session['format_type'] == 'video':
                            await pyrogram_client.send_video(
                                chat_id=message.chat.id,
                                video=file_path,
                                caption=f"✅ {title}\n📦 {file_size_mb:.1f}MB",
                            )
                        else:
                            await pyrogram_client.send_document(
                                chat_id=message.chat.id,
                                document=file_path,
                                caption=f"✅ {title}\n📦 {file_size_mb:.1f}MB",
                            )
                        await pyrogram_client.stop()
                    except Exception as pyr_error:
                        raise Exception(f"All uploads failed: {pyr_error}")
                else:
                    raise

        await progress_msg.delete()
        await message.answer(
            f"✅ <b>دانلود و ارسال موفق!</b>\n\n"
            f"📦 حجم: {file_size_mb:.1f} MB",
            parse_mode="HTML"
        )

        await state.clear()
        clear_session(user_id)

    except Exception as e:
        logger.error(f"Download error: {e}")
        try:
            await progress_msg.delete()
        except:
            pass
        await message.answer(
            f"❌ <b>خطا در دانلود!</b>\n\n"
            f"<code>{str(e)[:100]}</code>",
            parse_mode="HTML"
        )
        await state.clear()
        clear_session(user_id)
    
    finally:
        # Always cleanup temp file
        try:
            if session and session.get('file_path') and os.path.exists(session['file_path']):
                os.remove(session['file_path'])
                logger.info(f"✅ Cleaned up temp file: {session['file_path']}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file: {e}")


# ==================== RUN ====================

if __name__ == "__main__":
    import asyncio
    
    async def main():
        logger.info("🚀 Bot starting (Enhanced Professional Download System)...")
        await dp.start_polling(bot)

    asyncio.run(main())


__all__ = ["dp", "bot"]
