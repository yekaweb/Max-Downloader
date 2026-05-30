"""Download options keyboard"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_quality_keyboard() -> InlineKeyboardMarkup:
    """Create quality selection keyboard"""
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


__all__ = ["get_quality_keyboard"]
