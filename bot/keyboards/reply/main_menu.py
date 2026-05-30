"""Main menu reply keyboard"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    """Create main menu keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📥 Download")],
            [KeyboardButton(text="📜 History"), KeyboardButton(text="👤 Profile")],
            [KeyboardButton(text="🎁 Referral"), KeyboardButton(text="💳 Plans")],
            [KeyboardButton(text="⚙️ Settings"), KeyboardButton(text="❓ Help")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


__all__ = ["get_main_menu"]
