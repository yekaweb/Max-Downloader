"""Download options keyboard with exact file sizes"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict, Optional


def get_format_type_keyboard() -> InlineKeyboardMarkup:
    """Format Type Selection: Video or Audio"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎬 ویدیو", callback_data="format_video"),
                InlineKeyboardButton(text="🎵 صدا (Audio)", callback_data="format_audio"),
            ],
            [
                InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_download"),
            ],
            [
                InlineKeyboardButton(text="◀️ برگشت", callback_data="back_prev"),
            ],
        ]
    )


def get_video_quality_keyboard(format_info: Optional[Dict] = None) -> InlineKeyboardMarkup:
    """
    Video Quality Selection with EXACT file sizes
    
    Args:
        format_info: Dict with actual file sizes from yt-dlp
                    {"4k": {"size_mb": 2100.5}, "1080p": {"size_mb": 850.3}, ...}
    """
    buttons = []
    
    if not format_info:
        # Fallback to standard buttons if no format info provided
        buttons.append([InlineKeyboardButton(text="🔵 4K (2160p)", callback_data="quality_4k")])
        buttons.append([InlineKeyboardButton(text="🟢 1080p", callback_data="quality_1080")])
        buttons.append([InlineKeyboardButton(text="🟡 720p ✅", callback_data="quality_720")])
        buttons.append([InlineKeyboardButton(text="🟠 480p", callback_data="quality_480")])
        buttons.append([InlineKeyboardButton(text="🔴 360p", callback_data="quality_360")])
        buttons.append([InlineKeyboardButton(text="⚫ 240p", callback_data="quality_240")])
    else:
        # High Quality
        if "4k" in format_info:
            size = format_info["4k"].get("size_mb", 2100)
            text = f"🔵 4K (2160p) • {size:.1f} MB"
        else:
            text = "🔵 4K (2160p) • (غیر دسترس‌پذیر)"
        buttons.append([InlineKeyboardButton(text=text, callback_data="quality_4k" if "4k" in format_info else "quality_4k_na")])
        
        if "1080p" in format_info:
            size = format_info["1080p"].get("size_mb", 850)
            text = f"🟢 1080p • {size:.1f} MB"
        else:
            text = "🟢 1080p • (غیر دسترس‌پذیر)"
        buttons.append([InlineKeyboardButton(text=text, callback_data="quality_1080" if "1080p" in format_info else "quality_1080_na")])
        
        # Medium Quality
        if "720p" in format_info:
            size = format_info["720p"].get("size_mb", 420)
            text = f"🟡 720p • {size:.1f} MB ✅"
        else:
            text = "🟡 720p • (غیر دسترس‌پذیر) ✅"
        buttons.append([InlineKeyboardButton(text=text, callback_data="quality_720" if "720p" in format_info else "quality_720_na")])
        
        if "480p" in format_info:
            size = format_info["480p"].get("size_mb", 200)
            text = f"🟠 480p • {size:.1f} MB"
        else:
            text = "🟠 480p • (غیر دسترس‌پذیر)"
        buttons.append([InlineKeyboardButton(text=text, callback_data="quality_480" if "480p" in format_info else "quality_480_na")])
        
        # Low Quality
        if "360p" in format_info:
            size = format_info["360p"].get("size_mb", 95)
            text = f"🔴 360p • {size:.1f} MB"
        else:
            text = "🔴 360p • (غیر دسترس‌پذیر)"
        buttons.append([InlineKeyboardButton(text=text, callback_data="quality_360" if "360p" in format_info else "quality_360_na")])
        
        if "240p" in format_info:
            size = format_info["240p"].get("size_mb", 45)
            text = f"⚫ 240p • {size:.1f} MB"
        else:
            text = "⚫ 240p • (غیر دسترس‌پذیر)"
        buttons.append([InlineKeyboardButton(text=text, callback_data="quality_240" if "240p" in format_info else "quality_240_na")])
    
    # Back button
    buttons.append([InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_format")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_video_codec_keyboard(codec_sizes: Optional[Dict] = None) -> InlineKeyboardMarkup:
    """
    Video Codec Selection with EXACT file sizes
    
    Args:
        codec_sizes: Dict with file sizes per codec
                    {"h264": {"size_mb": 850.3}, "av1": {"size_mb": 520.5}, ...}
    """
    if codec_sizes is None:
        codec_sizes = {}
    
    buttons = []
    
    # H.264
    if "h264" in codec_sizes:
        size = codec_sizes["h264"].get("size_mb", 850)
        text = f"H.264 | MP4 ✅ سازگار • {size:.1f} MB"
    else:
        text = "H.264 | MP4 ✅ سازگار • (محاسبه‌شود)"
    buttons.append([InlineKeyboardButton(text=text, callback_data="codec_h264")])
    
    # AV1
    if "av1" in codec_sizes:
        size = codec_sizes["av1"].get("size_mb", 520)
        text = f"AV1 | WebM 🏆 کیفیت • {size:.1f} MB"
    else:
        text = "AV1 | WebM 🏆 کیفیت • (غیر موجود)"
    buttons.append([InlineKeyboardButton(text=text, callback_data="codec_av1" if "av1" in codec_sizes else "codec_av1_na")])
    
    # VP9
    if "vp9" in codec_sizes:
        size = codec_sizes["vp9"].get("size_mb", 610)
        text = f"VP9 | WebM ⚡ سبک • {size:.1f} MB"
    else:
        text = "VP9 | WebM ⚡ سبک • (غیر موجود)"
    buttons.append([InlineKeyboardButton(text=text, callback_data="codec_vp9" if "vp9" in codec_sizes else "codec_vp9_na")])
    
    buttons.append([InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_quality")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_subtitle_keyboard() -> InlineKeyboardMarkup:
    """Subtitle Selection with common languages"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="subtitle_fa"),
                InlineKeyboardButton(text="🇺🇸 English", callback_data="subtitle_en"),
            ],
            [
                InlineKeyboardButton(text="🇸🇦 عربی", callback_data="subtitle_ar"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="subtitle_ru"),
            ],
            [
                InlineKeyboardButton(text="✅ بدون زیرنویس", callback_data="subtitle_none"),
                InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_codec"),
            ],
        ]
    )


def get_send_as_keyboard() -> InlineKeyboardMarkup:
    """Send As Selection: Video or Document"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📹 ویدیو (قابل پخش)", callback_data="send_as_video")],
            [InlineKeyboardButton(text="📁 فایل (دانلود کامل)", callback_data="send_as_file")],
            [InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_subtitle")],
        ]
    )


def get_audio_format_keyboard() -> InlineKeyboardMarkup:
    """Audio Format Selection"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎼 MP3 320kbps • ~8MB/min", callback_data="audio_mp3_320")],
            [InlineKeyboardButton(text="🎼 MP3 128kbps • ~4MB/min", callback_data="audio_mp3_128")],
            [InlineKeyboardButton(text="🎧 AAC 256kbps • ~7MB/min", callback_data="audio_aac_256")],
            [InlineKeyboardButton(text="🎧 M4A 128kbps • ~3.5MB/min", callback_data="audio_m4a_128")],
            [InlineKeyboardButton(text="🔊 OPUS (بهترین) • ~3MB/min", callback_data="audio_opus")],
            [InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_format")],
        ]
    )


def get_quality_keyboard() -> InlineKeyboardMarkup:
    """Legacy quality keyboard for backward compatibility"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎬 HD (1080p)", callback_data="quality_1080"),
                InlineKeyboardButton(text="📺 SD (720p)", callback_data="quality_720"),
            ],
            [
                InlineKeyboardButton(text="📹 480p", callback_data="quality_480"),
                InlineKeyboardButton(text="📱 360p", callback_data="quality_360"),
            ],
            [
                InlineKeyboardButton(text="🎵 Audio Only", callback_data="quality_audio"),
                InlineKeyboardButton(text="⬅️ Back", callback_data="back"),
            ],
        ]
    )


__all__ = ["get_format_type_keyboard", "get_video_quality_keyboard", 
           "get_video_codec_keyboard", "get_subtitle_keyboard", 
           "get_send_as_keyboard", "get_audio_format_keyboard", 
           "get_quality_keyboard"]
