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
    Displays all available resolutions (from 4K down to 144p) with size labels.

    Args:
        format_info: Dict from get_exact_format_sizes() or get_exact_format_sizes()["video_formats"]
    """
    buttons = []

    quality_order = [
        ("4k",    "🔵 4K (2160p)"),
        ("1440p", "🟣 1440p (2K)"),
        ("1080p", "🟢 1080p (FHD)"),
        ("720p",  "🟡 720p (HD) ✅"),
        ("480p",  "🟠 480p (SD)"),
        ("360p",  "🔴 360p"),
        ("240p",  "⚫ 240p"),
        ("144p",  "⚪ 144p"),
    ]
    cb_map = {
        "4k": "quality_4k",
        "1440p": "quality_1440",
        "1080p": "quality_1080",
        "720p":  "quality_720",
        "480p":  "quality_480",
        "360p":  "quality_360",
        "240p":  "quality_240",
        "144p":  "quality_144",
    }

    video_fmts = {}
    if isinstance(format_info, dict):
        video_fmts = format_info.get("video_formats", format_info)

    if video_fmts:
        for key, label in quality_order:
            if key not in video_fmts:
                continue
            fmt_data = video_fmts[key]
            size = fmt_data.get("size_mb") if isinstance(fmt_data, dict) else None
            size_str = f"{size:.1f} MB" if size else "حجم: تقریبی"
            buttons.append([InlineKeyboardButton(
                text=f"{label} • {size_str}",
                callback_data=cb_map[key],
            )])

    # Fallback default qualities if metadata parsing didn't find specific heights
    if not buttons:
        default_qualities = [
            ("1080p", "🟢 1080p (FHD)"),
            ("720p",  "🟡 720p (HD) ✅"),
            ("480p",  "🟠 480p (SD)"),
            ("360p",  "🔴 360p"),
        ]
        for key, label in default_qualities:
            buttons.append([InlineKeyboardButton(
                text=label,
                callback_data=cb_map[key],
            )])

    # Back button to format selection
    buttons.append([InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_format")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_video_codec_keyboard(codec_sizes: Optional[Dict] = None) -> InlineKeyboardMarkup:
    """
    Video Codec Selection with clear compatibility notes and sizes.

    Args:
        codec_sizes: Dict with file sizes per codec (from format_info["codec_sizes"])
    """
    if codec_sizes is None:
        codec_sizes = {}
    elif isinstance(codec_sizes, dict) and "codec_sizes" in codec_sizes:
        codec_sizes = codec_sizes["codec_sizes"]

    buttons = []

    # H.264 — always shown, universal compatibility
    h264_info = codec_sizes.get("h264") if isinstance(codec_sizes, dict) else None
    h264_sz = h264_info.get("size_mb") if isinstance(h264_info, dict) else None
    h264_str = f" • ~{h264_sz:.1f} MB" if h264_sz else ""
    buttons.append([InlineKeyboardButton(
        text=f"H.264 | MP4 ✅ سازگار با همه{h264_str}",
        callback_data="codec_h264"
    )])

    # AV1 — high efficiency
    av1_info = codec_sizes.get("av1") if isinstance(codec_sizes, dict) else None
    av1_sz = av1_info.get("size_mb") if isinstance(av1_info, dict) else None
    av1_str = f" • ~{av1_sz:.1f} MB" if av1_sz else ""
    buttons.append([InlineKeyboardButton(
        text=f"AV1 | WebM 🏆 بهترین کیفیت{av1_str}",
        callback_data="codec_av1"
    )])

    # VP9 — lightweight
    vp9_info = codec_sizes.get("vp9") if isinstance(codec_sizes, dict) else None
    vp9_sz = vp9_info.get("size_mb") if isinstance(vp9_info, dict) else None
    vp9_str = f" • ~{vp9_sz:.1f} MB" if vp9_sz else ""
    buttons.append([InlineKeyboardButton(
        text=f"VP9 | WebM ⚡ سبک و سریع{vp9_str}",
        callback_data="codec_vp9"
    )])

    # Back button goes back to video quality selection
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
