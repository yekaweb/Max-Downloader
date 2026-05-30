"""Admin menu reply keyboard"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_admin_menu() -> ReplyKeyboardMarkup:
    """Create admin menu keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Stats")],
            [KeyboardButton(text="👥 Users"), KeyboardButton(text="📢 Broadcast")],
            [KeyboardButton(text="💳 Plans"), KeyboardButton(text="🔗 Channels")],
            [KeyboardButton(text="🔙 Back")],
        ],
        resize_keyboard=True,
    )


__all__ = ["get_admin_menu"]
