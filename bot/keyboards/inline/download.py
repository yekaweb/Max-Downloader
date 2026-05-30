"""Download options keyboard"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


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
        ]
    )


def get_video_quality_keyboard() -> InlineKeyboardMarkup:
    """Video Quality Selection - Grouped by tier"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # High Quality
            [InlineKeyboardButton(text="🔵 4K (2160p) • ~2.1GB", callback_data="quality_4k")],
            [InlineKeyboardButton(text="🟢 1080p • ~850MB", callback_data="quality_1080")],
            # Medium Quality
            [InlineKeyboardButton(text="🟡 720p • ~420MB ✅", callback_data="quality_720")],
            [InlineKeyboardButton(text="🟠 480p • ~200MB", callback_data="quality_480")],
            # Low Quality
            [InlineKeyboardButton(text="🔴 360p • ~95MB", callback_data="quality_360")],
            [InlineKeyboardButton(text="⚫ 240p • ~45MB", callback_data="quality_240")],
            # Back button
            [InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_format")],
        ]
    )


def get_video_codec_keyboard() -> InlineKeyboardMarkup:
    """Video Codec Selection"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="H.264 | MP4 ✅ سازگار", callback_data="codec_h264")],
            [InlineKeyboardButton(text="AV1 | WebM 🏆 کیفیت", callback_data="codec_av1")],
            [InlineKeyboardButton(text="VP9 | WebM ⚡ سبک", callback_data="codec_vp9")],
            [InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_quality")],
        ]
    )


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
