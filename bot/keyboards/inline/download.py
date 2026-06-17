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
    Video Quality Selection with EXACT file sizes.
    Only shows quality buttons for resolutions that actually exist in format_info.

    Args:
        format_info: Dict from get_exact_format_sizes()["video_formats"]
                    {"480p": {"size_mb": 8.9 | None, ...}, ...}
    """
    buttons = []

    if format_info:
        quality_order = [
            ("4k",    "🔵 4K (2160p)"),
            ("1440p", "🟣 1440p"),
            ("1080p", "🟢 1080p"),
            ("720p",  "🟡 720p ✅"),
            ("480p",  "🟠 480p"),
            ("360p",  "🔴 360p"),
            ("240p",  "⚫ 240p"),
        ]
        # Callback keys do NOT include the trailing 'p' for consistency with quality_map
        cb_map = {
            "4k": "quality_4k",
            "1440p": "quality_1440",
            "1080p": "quality_1080",
            "720p":  "quality_720",
            "480p":  "quality_480",
            "360p":  "quality_360",
            "240p":  "quality_240",
        }
        for key, label in quality_order:
            if key not in format_info:
                continue
            # FIX Bug #7: size_mb may be None
            size = format_info[key].get("size_mb")
            size_str = f"{size:.1f} MB" if size else "حجم: نامشخص"
            buttons.append([InlineKeyboardButton(
                text=f"{label} • {size_str}",
                callback_data=cb_map[key],
            )])

    # Back button always present
    buttons.append([InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_format")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_video_codec_keyboard(codec_sizes: Optional[Dict] = None) -> InlineKeyboardMarkup:
    """
    Video Codec Selection with EXACT file sizes.

    Args:
        codec_sizes: Dict with file sizes per codec (from format_info["codec_sizes"])
                    {"h264": {"size_mb": 850.3}, "av1": {"size_mb": 520.5}, ...}
    """
    if codec_sizes is None:
        codec_sizes = {}

    buttons = []

    # H.264 — always shown, most compatible
    if "h264" in codec_sizes:
        size = codec_sizes["h264"].get("size_mb")
        size_str = f"{size:.1f} MB" if size else "حجم: نامشخص"
        text = f"H.264 | MP4 ✅ سازگار • {size_str}"
    else:
        text = "H.264 | MP4 ✅ سازگار"
    buttons.append([InlineKeyboardButton(text=text, callback_data="codec_h264")])

    # AV1 — only if available
    if "av1" in codec_sizes:
        size = codec_sizes["av1"].get("size_mb")
        size_str = f"{size:.1f} MB" if size else "حجم: نامشخص"
        buttons.append([InlineKeyboardButton(text=f"AV1 | WebM 🏆 کیفیت • {size_str}", callback_data="codec_av1")])

    # VP9 — only if available
    if "vp9" in codec_sizes:
        size = codec_sizes["vp9"].get("size_mb")
        size_str = f"{size:.1f} MB" if size else "حجم: نامشخص"
        buttons.append([InlineKeyboardButton(text=f"VP9 | WebM ⚡ سبک • {size_str}", callback_data="codec_vp9")])

    # FIX Bug #3.2: back button goes to format-type selection, NOT quality
    buttons.append([InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_format")])

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


def get_send_as_keyboard(has_dubbed: bool = False) -> InlineKeyboardMarkup:
    """Send As Selection: Video or Document"""
    # Back button goes to language selection if dubbed tracks exist, else subtitle
    back_cb = "back_to_language" if has_dubbed else "back_to_subtitle"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📹 ویدیو (قابل پخش)", callback_data="send_as_video")],
            [InlineKeyboardButton(text="📁 فایل (دانلود کامل)", callback_data="send_as_file")],
            [InlineKeyboardButton(text="◀️ برگشت", callback_data=back_cb)],
        ]
    )


def get_dubbed_language_keyboard(dubbed_tracks: dict) -> InlineKeyboardMarkup:
    """
    Phase 5.2 — Dubbed / Multi-language Audio Track Selection.

    Args:
        dubbed_tracks: from format_info['dubbed_tracks']
            {'en': {'name': 'English 🇺🇸', 'format_id': '...'}, 'fa': {...}, ...}
    """
    buttons = []
    for lang_code, info in dubbed_tracks.items():
        name = info.get('name', lang_code.upper())
        size = info.get('size_mb')
        size_str = f" • {size:.1f} MB" if size else ""
        buttons.append([InlineKeyboardButton(
            text=f"🔊 {name}{size_str}",
            callback_data=f"lang_{lang_code}",
        )])
    # Option to skip and use original audio
    buttons.append([InlineKeyboardButton(
        text="🎵 صدای اصلی ویدیو (پیش‌فرض)",
        callback_data="lang_original",
    )])
    buttons.append([InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_subtitle")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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
           "get_send_as_keyboard", "get_dubbed_language_keyboard",
           "get_audio_format_keyboard", "get_quality_keyboard"]
