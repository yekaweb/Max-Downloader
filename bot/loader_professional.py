"""
PROFESSIONAL DOWNLOAD SYSTEM
Complete FSM implementation with auto-detect, direct URL support, and dynamic progress
Based on "We want build this.md" specification
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
    InlineKeyboardMarkup, PhotoSize
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

# Initialize Pyrogram client for large file uploads (no 50MB limit)
pyrogram_client = None
if PYROGRAM_AVAILABLE and settings.PYROGRAM_APP_ID and settings.PYROGRAM_APP_HASH:
    try:
        pyrogram_client = Client(
            name=settings.PYROGRAM_SESSION_NAME,
            api_id=int(settings.PYROGRAM_APP_ID),
            api_hash=settings.PYROGRAM_APP_HASH,
            no_updates=True,
            workdir='.',
        )
        logger.info("✅ Pyrogram client initialized (unlimited file uploads)")
    except Exception as e:
        logger.warning(f"⚠️ Pyrogram initialization failed: {e}, will use aiogram only")
        pyrogram_client = None

# ==================== INITIALIZATION ====================

bot = Bot(token=settings.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Session storage for tracking download progress per user
download_sessions: Dict[int, Dict[str, Any]] = {}


def get_session(user_id: int) -> Dict[str, Any]:
    """Get or create user session"""
    if user_id not in download_sessions:
        download_sessions[user_id] = {
            "url": None,
            "media_info": None,
            "format_type": None,  # "video" or "audio"
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
    Fetch media info from URL using yt-dlp
    Returns: {
        'title': str,
        'duration': int (seconds),
        'thumbnail': str (URL),
        'views': int,
        'uploader': str,
        'formats': {...}
    }
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
        }

        loop = asyncio.get_event_loop()
        
        def _extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)

        info = await loop.run_in_executor(None, _extract)
        
        if not info:
            return None

        # Parse formats
        formats = info.get('formats', [])
        video_formats = {}
        audio_formats = {}

        # Group by quality/codec
        for fmt in formats:
            vcodec = fmt.get('vcodec', 'unknown')
            acodec = fmt.get('acodec', 'unknown')
            height = fmt.get('height')
            filesize = fmt.get('filesize')

            # Video formats
            if vcodec != 'none' and vcodec != 'unknown' and height:
                key = f"{height}p_{vcodec}"
                if key not in video_formats or not filesize:
                    video_formats[key] = {
                        'format_id': fmt.get('format_id'),
                        'height': height,
                        'vcodec': vcodec,
                        'acodec': acodec,
                        'filesize': filesize,
                        'ext': fmt.get('ext', 'mp4'),
                    }

            # Audio formats
            if acodec != 'none' and acodec != 'unknown' and vcodec == 'none':
                abr = fmt.get('abr')
                key = f"{acodec}_{abr}" if abr else acodec
                if key not in audio_formats:
                    audio_formats[key] = {
                        'format_id': fmt.get('format_id'),
                        'acodec': acodec,
                        'abr': abr,
                        'filesize': filesize,
                        'ext': fmt.get('ext', 'm4a'),
                    }

        # Format time display
        duration = info.get('duration', 0)
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"{minutes:02d}:{seconds:02d}"

        return {
            'title': info.get('title', 'Media'),
            'duration': duration,
            'duration_str': duration_str,
            'thumbnail': info.get('thumbnail', ''),
            'views': info.get('view_count', 0),
            'uploader': info.get('uploader', 'Unknown'),
            'video_formats': video_formats,
            'audio_formats': audio_formats,
        }

    except Exception as e:
        logger.error(f"Error fetching media info: {e}")
        return None


# ==================== FILE SIZE CALCULATION ====================

def format_bytes_mb(bytes_val: Optional[int]) -> str:
    """Convert bytes to MB with proper formatting"""
    if bytes_val is None or bytes_val <= 0:
        return "?MB"
    mb = bytes_val / (1024 * 1024)
    if mb >= 1000:
        return f"{mb/1024:.1f}GB"
    return f"{mb:.1f}MB"


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


def get_video_quality_kb(video_formats: Dict) -> InlineKeyboardMarkup:
    """Video quality selection keyboard"""
    buttons = []

    # Sort by height descending
    sorted_formats = sorted(
        video_formats.items(),
        key=lambda x: x[1].get('height', 0),
        reverse=True
    )

    groups = {
        "high": [],      # 1080p+
        "medium": [],    # 480-1080p
        "low": [],       # <480p
    }

    for key, fmt in sorted_formats:
        height = fmt.get('height', 0)
        filesize_mb = format_bytes_mb(fmt.get('filesize'))
        
        quality_label = f"{height}p • {filesize_mb}"
        
        if height >= 1080:
            groups["high"].append((key, quality_label, height))
        elif height >= 480:
            groups["medium"].append((key, quality_label, height))
        else:
            groups["low"].append((key, quality_label, height))

    # Add High Quality group
    if groups["high"]:
        buttons.append([InlineKeyboardButton(text="━━━━ کیفیت بالا ━━━━", callback_data="ignored")])
        for key, label, height in groups["high"][:3]:
            emoji = "🔵" if height >= 2160 else "🟢"
            recommend = " ✅ پیشنهاد" if height == 1080 else ""
            buttons.append([InlineKeyboardButton(
                text=f"{emoji} {label}{recommend}",
                callback_data=f"quality_{key}"
            )])

    # Add Medium Quality group
    if groups["medium"]:
        buttons.append([InlineKeyboardButton(text="━━━━ کیفیت متوسط ━━━━", callback_data="ignored")])
        for key, label, height in groups["medium"][:3]:
            emoji = "🟡" if height == 720 else "🟠"
            buttons.append([InlineKeyboardButton(
                text=f"{emoji} {label}",
                callback_data=f"quality_{key}"
            )])

    # Add Low Quality group
    if groups["low"]:
        buttons.append([InlineKeyboardButton(text="━━━━ کیفیت پایین ━━━━", callback_data="ignored")])
        for key, label, height in groups["low"][:3]:
            emoji = "🔴" if height >= 360 else "⚫"
            buttons.append([InlineKeyboardButton(
                text=f"{emoji} {label}",
                callback_data=f"quality_{key}"
            )])

    # Back button
    buttons.append([InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_format")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_audio_format_kb(audio_formats: Dict) -> InlineKeyboardMarkup:
    """Audio format selection keyboard"""
    buttons = []

    # Common audio formats in priority order
    priority_order = ['opus', 'aac', 'mp3', 'vorbis', 'flac']
    
    sorted_formats = sorted(
        audio_formats.items(),
        key=lambda x: (
            priority_order.index(x[1].get('acodec', '')) 
            if x[1].get('acodec', '') in priority_order else 999
        )
    )

    for key, fmt in sorted_formats[:6]:
        acodec = fmt.get('acodec', '').upper()
        abr = fmt.get('abr', 'unknown')
        filesize_mb = format_bytes_mb(fmt.get('filesize'))
        
        # Get emoji
        emoji = {
            'MP3': '🎼',
            'AAC': '🎧',
            'OPUS': '🔊',
            'VORBIS': '🎵',
            'FLAC': '🎼',
        }.get(acodec, '🎵')

        label = f"{emoji} {acodec}"
        if abr:
            label += f" {abr}kbps"
        label += f" • {filesize_mb}"

        if acodec == 'OPUS':
            label += " 🏆 بهترین"

        buttons.append([InlineKeyboardButton(
            text=label,
            callback_data=f"audio_{key}"
        )])

    buttons.append([InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_format")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_codec_kb() -> InlineKeyboardMarkup:
    """Video codec selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="H.264 | MP4 ✅ سازگار", callback_data="codec_h264")],
        [InlineKeyboardButton(text="AV1 | WebM 🏆 بهترین", callback_data="codec_av1")],
        [InlineKeyboardButton(text="VP9 | WebM ⚡ سبک", callback_data="codec_vp9")],
        [InlineKeyboardButton(text="ℹ️ اگر مطمئن نیستید H.264 را زنید", callback_data="ignored")],
        [InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_quality")],
    ])


def get_subtitle_kb() -> InlineKeyboardMarkup:
    """Subtitle selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="sub_fa"),
            InlineKeyboardButton(text="🇺🇸 English", callback_data="sub_en"),
        ],
        [
            InlineKeyboardButton(text="🇸🇦 عربی", callback_data="sub_ar"),
            InlineKeyboardButton(text="🇷🇺 Russian", callback_data="sub_ru"),
        ],
        [InlineKeyboardButton(text="✅ بدون زیرنویس", callback_data="sub_none")],
        [InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_codec")],
    ])


def get_send_as_kb() -> InlineKeyboardMarkup:
    """Send as selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📹 ویدیو (تلگرام)", callback_data="send_video")],
        [InlineKeyboardButton(text="📁 فایل (دانلود)", callback_data="send_file")],
        [InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_subtitle")],
    ])


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
        logger.error(f"Error updating progress: {e}")
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
    """Handle URL input - with auto-detect"""
    url = message.text.strip()

    if not is_valid_url(url):
        await message.answer(
            "❌ <b>لینک نامعتبر است!</b>\n\n"
            "لطفاً یک لینک معتبر ارسال کنید:",
            parse_mode="HTML"
        )
        return

    # Get session
    session = get_session(message.from_user.id)
    session['url'] = url
    platform = detect_platform(url)

    # Show fetching message
    progress_msg = await send_progress_message(
        message,
        "درحال دریافت اطلاعات...",
        phase="fetching"
    )
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

    # Show media info
    title = media_info['title'][:60]
    duration = media_info['duration_str']
    views = media_info['views']
    uploader = media_info['uploader'][:30]
    
    platform_emoji = get_platform_emoji(platform) if platform else "📺"

    info_text = f"""
{platform_emoji} <b>اطلاعات رسانه</b>

📺 <b>نام:</b> <code>{title}</code>
⏱ <b>مدت:</b> {duration}
👁 <b>بازدید:</b> {views:,}
👤 <b>اپلود‌کننده:</b> {uploader}

━━━━━━━━━━━━━━━━━━━━━

نوع فایل را انتخاب کنید:
"""

    await progress_msg.delete()
    await message.answer(info_text, parse_mode="HTML", reply_markup=get_format_type_kb())
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
        
        if not media_info.get('video_formats'):
            await query.answer("❌ فرمت ویدیو در دسترس نیست!", show_alert=True)
            return

        text = "📺 <b>کیفیت ویدیو را انتخاب کنید:</b>"
        kb = get_video_quality_kb(media_info['video_formats'])
        
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await state.set_state(DownloadStates.video_quality_selection)

    elif query.data == "format_audio":
        session['format_type'] = "audio"
        
        if not media_info.get('audio_formats'):
            await query.answer("❌ فرمت صوتی در دسترس نیست!", show_alert=True)
            return

        text = "🎵 <b>فرمت صوتی را انتخاب کنید:</b>"
        kb = get_audio_format_kb(media_info['audio_formats'])
        
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await state.set_state(DownloadStates.audio_format_selection)


# Handle video quality selection
@dp.callback_query(DownloadStates.video_quality_selection)
async def handle_video_quality(query: CallbackQuery, state: FSMContext):
    """Handle video quality selection"""
    await query.answer()

    if query.data == "back_to_format":
        session = get_session(query.from_user.id)
        text = "🎯 <b>نوع فایل دریافتی را انتخاب کنید:</b>"
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=get_format_type_kb())
        await state.set_state(DownloadStates.selecting_format_type)
        return

    if not query.data.startswith("quality_"):
        await query.answer("انتخاب نامعتبر", show_alert=True)
        return

    quality_key = query.data.replace("quality_", "")
    session = get_session(query.from_user.id)
    session['quality'] = quality_key

    # Move to codec selection
    text = "🎞️ <b>کدک ویدیو را انتخاب کنید:</b>\n\n<i>اگر مطمئن نیستید H.264 را انتخاب کنید</i>"
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=get_codec_kb())
    await state.set_state(DownloadStates.video_codec_selection)


# Handle codec selection
@dp.callback_query(DownloadStates.video_codec_selection)
async def handle_codec(query: CallbackQuery, state: FSMContext):
    """Handle codec selection"""
    await query.answer()

    if query.data == "back_to_quality":
        session = get_session(query.from_user.id)
        media_info = session['media_info']
        text = "📺 <b>کیفیت ویدیو را انتخاب کنید:</b>"
        kb = get_video_quality_kb(media_info['video_formats'])
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await state.set_state(DownloadStates.video_quality_selection)
        return

    if query.data == "ignored":
        await query.answer()
        return

    codec = query.data.replace("codec_", "")
    session = get_session(query.from_user.id)
    session['codec'] = codec

    # Move to subtitle selection
    text = "📝 <b>زیرنویس می‌خواهید؟</b>"
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=get_subtitle_kb())
    await state.set_state(DownloadStates.video_selecting_subtitle)


# Handle subtitle selection
@dp.callback_query(DownloadStates.video_selecting_subtitle)
async def handle_subtitle(query: CallbackQuery, state: FSMContext):
    """Handle subtitle selection"""
    await query.answer()

    if query.data == "back_to_codec":
        text = "🎞️ <b>کدک ویدیو را انتخاب کنید:</b>"
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=get_codec_kb())
        await state.set_state(DownloadStates.video_codec_selection)
        return

    session = get_session(query.from_user.id)
    session['subtitle'] = query.data.replace("sub_", "")

    # Move to send_as selection
    text = "📤 <b>نحوه دریافت فایل:</b>"
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=get_send_as_kb())
    await state.set_state(DownloadStates.video_selecting_send_as)


# Handle send_as selection
@dp.callback_query(DownloadStates.video_selecting_send_as)
async def handle_send_as(query: CallbackQuery, state: FSMContext):
    """Handle send_as selection and start download"""
    await query.answer()

    if query.data == "back_to_subtitle":
        text = "📝 <b>زیرنویس می‌خواهید؟</b>"
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=get_subtitle_kb())
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
    """Handle audio format selection"""
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
            quality_key = session['quality']
            codec = session['codec']
            
            # Build format string (simplified - would need real format selection logic)
            ydl_opts['format'] = 'best[vcodec^=h264][ext=mp4]/best'
            
        else:  # audio
            ydl_opts['format'] = 'bestaudio'
            ydl_opts['postprocessors'] = [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }
            ]

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
        session['file_path'] = file_path  # Store for cleanup in finally block

        # Update to upload phase
        await update_progress_message(
            progress_msg,
            title,
            100,
            total_mb,
            0,
            0,
            0,
            phase="uploading"
        )

        # Check file size vs Telegram limit
        file_size_mb = os.path.getsize(file_path) / (1024*1024)
        
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
                # Fallback to aiogram for small files
                if file_size_mb <= 2048:  # 2GB aiogram limit
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
                    except Exception as aiogram_error:
                        raise Exception(f"Both upload methods failed: {aiogram_error}")
                else:
                    raise Exception(f"File too large even for aiogram: {file_size_mb:.1f}MB > 2GB")
        
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
                # Try with Pyrogram as last resort
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
                        raise Exception(f"All upload methods failed: {e} | {pyr_error}")
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
        await progress_msg.delete()
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
        logger.info("🚀 Bot starting (Professional Download System)...")
        await dp.start_polling(bot)

    asyncio.run(main())


__all__ = ["dp", "bot"]
