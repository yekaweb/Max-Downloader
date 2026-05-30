"""Inline Keyboards for DLBot"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_kb() -> InlineKeyboardMarkup:
    """منوی اصلی"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📥 دانلود ویدیو",
                    callback_data="download_menu"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👤 پروفایل",
                    callback_data="profile"
                ),
                InlineKeyboardButton(
                    text="⚙️ تنظیمات",
                    callback_data="settings"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📚 راهنما",
                    callback_data="guide"
                ),
                InlineKeyboardButton(
                    text="❓ درباره",
                    callback_data="about_menu"
                )
            ]
        ]
    )
    return kb


def download_platform_kb() -> InlineKeyboardMarkup:
    """انتخاب پلتفرم"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎥 YouTube",
                    callback_data="platform_youtube"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📸 Instagram",
                    callback_data="platform_instagram"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🐦 Twitter",
                    callback_data="platform_twitter"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 بازگشت به منوی اصلی",
                    callback_data="back_main"
                )
            ]
        ]
    )
    return kb


def admin_menu_kb() -> InlineKeyboardMarkup:
    """منوی ادمین"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 آمار",
                    callback_data="admin_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Broadcast",
                    callback_data="admin_broadcast"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 کاربران",
                    callback_data="admin_users"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 بازگشت به منوی اصلی",
                    callback_data="back_main"
                )
            ]
        ]
    )
    return kb


def language_kb() -> InlineKeyboardMarkup:
    """انتخاب زبان"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇮🇷 فارسی",
                    callback_data="lang_fa"
                ),
                InlineKeyboardButton(
                    text="🇺🇸 English",
                    callback_data="lang_en"
                )
            ]
        ]
    )
    return kb

__all__ = [
    "main_menu_kb",
    "download_platform_kb",
    "admin_menu_kb",
    "language_kb"
]
