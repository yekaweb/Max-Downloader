"""
Pro Cache Inline Keyboards
کیبوردهای اینلاین سه دکمه‌ای برای سیستم کش هوشمند
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from database.models.cached_download import CachedQuality


class CacheKeyboards:
    """کیبوردهای مربوط به نمایش و انتخاب فایل‌های کش شده"""

    @staticmethod
    def main_cache_options_keyboard(
        quality_count: int,
        url_hash: str
    ) -> InlineKeyboardMarkup:
        """
        کیبورد اصلی سه دکمه‌ای:
        1️⃣  N کیفیت از این ویدیو در آرشیو موجوده (دریافت سریع)
        2️⃣  پیدا کردن کیفیت‌های جدید
        3️⃣  بازگشت
        """
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"📚 {quality_count} کیفیت از این ویدیو در آرشیو موجوده (دریافت سریع)",
                    callback_data=f"show_cached:{url_hash}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 پیدا کردن کیفیت‌های جدید",
                    callback_data=f"download_new:{url_hash}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 بازگشت",
                    callback_data="back_to_main"
                )
            ]
        ])

    @staticmethod
    def cached_qualities_keyboard(
        qualities: List[CachedQuality],
        show_back: bool = True
    ) -> InlineKeyboardMarkup:
        """
        کیبورد نمایش کیفیت‌های کش شده
        هر دکمه = یک کیفیت قابل دریافت
        """
        keyboard_buttons = []

        # جدا کردن کیفیت‌های ویدیویی و صوتی
        video_quals = [q for q in qualities if q.mime_type and 'audio' not in q.mime_type]
        audio_quals = [q for q in qualities if q.mime_type and 'audio' in q.mime_type]

        # مرتب‌سازی ویدیوها بر اساس resolution (بالا به پایین)
        def _sort_key_video(q: CachedQuality):
            if q.resolution and 'x' in q.resolution:
                try:
                    return int(q.resolution.split('x')[1])
                except:
                    return 0
            return 0

        video_quals.sort(key=_sort_key_video, reverse=True)

        # مرتب‌سازی صداها بر اساس bitrate (بالا به پایین)
        audio_quals.sort(key=lambda q: q.bitrate or 0, reverse=True)

        # اضافه کردن کیفیت‌های ویدیو
        for q in video_quals:
            size_text = f"{q.file_size_mb:.1f} MB" if q.file_size else "?"
            codec_icon = _get_codec_icon(q.video_codec)
            text = f"🎬 {q.quality_label} {codec_icon} • {size_text} • {q.extension or ''}"
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=text.strip(),
                    callback_data=f"send_cached:{q.id}"
                )
            ])

        # جداکننده صوتی
        if video_quals and audio_quals:
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text="━━━ 🎵 فایل‌های صوتی ━━━",
                    callback_data="separator"
                )
            ])

        # اضافه کردن کیفیت‌های صوتی
        for q in audio_quals:
            size_text = f"{q.file_size_mb:.1f} MB" if q.file_size else "?"
            text = f"🎵 {q.quality_label} • {size_text} • {q.extension or ''}"
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=text.strip(),
                    callback_data=f"send_cached:{q.id}"
                )
            ])

        # دکمه بازگشت
        if show_back:
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text="◀️ بازگشت",
                    callback_data="back_to_cache_options"
                )
            ])

        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    @staticmethod
    def fresh_search_keyboard() -> InlineKeyboardMarkup:
        """کیبورد ساده برای شروع دانلود جدید"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 دانلود جدید",
                    callback_data="fresh_search"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 بازگشت",
                    callback_data="back_to_main"
                )
            ]
        ])


def _get_codec_icon(codec: str) -> str:
    """دریافت آیکون مناسب برای codec"""
    if not codec:
        return ""
    codec_lower = codec.lower()
    icons = {
        'h264': '📹', 'h265': '🎥', 'vp9': '🎞', 'av1': '🎯',
        'aac': '🔊', 'opus': '🎧', 'mp3': '🎼'
    }
    for key, icon in icons.items():
        if key in codec_lower:
            return icon
    return ''


__all__ = ["CacheKeyboards", "get_cache_options_keyboard", "get_cached_qualities_keyboard"]


# Convenience function aliases
def get_cache_options_keyboard(quality_count: int, url_hash: str) -> InlineKeyboardMarkup:
    """Convenience: 3-button main cache keyboard"""
    return CacheKeyboards.main_cache_options_keyboard(quality_count, url_hash)


def get_cached_qualities_keyboard(qualities: List[CachedQuality]) -> InlineKeyboardMarkup:
    """Convenience: qualities selection keyboard"""
    return CacheKeyboards.cached_qualities_keyboard(qualities)
