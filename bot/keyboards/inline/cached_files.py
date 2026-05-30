"""
Cached Downloads Keyboard
Interactive buttons for selecting cached files
"""

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.models.cached_download import CachedDownload


def get_cached_files_keyboard(cached_downloads: List[CachedDownload]) -> InlineKeyboardMarkup:
    """
    Create interactive keyboard for selecting cached files
    
    Layout:
    [1️⃣ 1080p] [2️⃣ 720p]
    [3️⃣ 480p]  [4️⃣ Audio]
    
    [🆕 دانلود فرمت جدید]
    [❌ لغو]
    """
    
    builder = []
    
    # Add cached file buttons (max 2 per row)
    for idx, cached in enumerate(cached_downloads, 1):
        button_text = f"{idx}️⃣ {cached.quality}\n{cached.file_size_mb:.1f}MB"
        callback_data = f"cache_select:{cached.id}"
        
        if len(builder) == 0 or len(builder[-1]) >= 2:
            builder.append([])
        
        builder[-1].append(
            InlineKeyboardButton(
                text=button_text,
                callback_data=callback_data
            )
        )
    
    # Add action buttons
    builder.append([
        InlineKeyboardButton(
            text="🆕 دانلود فرمت جدید",
            callback_data="cache_new_format"
        )
    ])
    
    builder.append([
        InlineKeyboardButton(
            text="❌ لغو",
            callback_data="download_cancel"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=builder)


def get_cache_action_keyboard() -> InlineKeyboardMarkup:
    """
    Get keyboard for cached file actions (after selection)
    
    [✅ دانلود]  [🔄 فرمت دیگر]  [❌ حذف]
    """
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ دانلود", callback_data="cache_download"),
                InlineKeyboardButton(text="🔄 فرمت دیگر", callback_data="cache_new_format"),
                InlineKeyboardButton(text="❌ حذف", callback_data="cache_delete"),
            ],
            [
                InlineKeyboardButton(text="◀️ برگشت", callback_data="cache_back"),
            ]
        ]
    )


def get_cache_format_options_keyboard() -> InlineKeyboardMarkup:
    """
    Get keyboard for selecting new format to download
    
    [🎬 ویدیو]  [🎵 صدا]
    [❌ لغو]
    """
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎬 ویدیو", callback_data="cache_format_video"),
                InlineKeyboardButton(text="🎵 صدا", callback_data="cache_format_audio"),
            ],
            [
                InlineKeyboardButton(text="❌ لغو", callback_data="download_cancel"),
            ]
        ]
    )


__all__ = [
    "get_cached_files_keyboard",
    "get_cache_action_keyboard",
    "get_cache_format_options_keyboard",
]
