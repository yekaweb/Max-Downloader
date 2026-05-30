"""Language/i18n selection keyboard"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Create language selection keyboard"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="lang_fa"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            ],
            [
                InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang_ar"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            ],
            [
                InlineKeyboardButton(text="🇨🇳 中文", callback_data="lang_zh"),
            ],
        ]
    )


__all__ = ["get_language_keyboard"]
