"""
Beautiful Glassmorphism Keyboards for DLBot
Provides modern, transparent UI with blur effect
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Optional

class GlassKeyboards:
    """Modern glassmorphism keyboard builder"""
    
    # Main Menu
    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """Beautiful main menu with glassmorphism style"""
        buttons = [
            [
                KeyboardButton(text="⬇️ دانلود"),  # Download
                KeyboardButton(text="💎 سکه های من"),  # My Coins
            ],
            [
                KeyboardButton(text="👥 دعوت دوستان"),  # Invite Friends
                KeyboardButton(text="📊 پروفایل"),  # Profile
            ],
            [
                KeyboardButton(text="ℹ️ کمک"),  # Help
                KeyboardButton(text="⚙️ تنظیمات"),  # Settings
            ]
        ]
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True,
            is_persistent=True,
            selective=True
        )
    
    # Download Quality Selection (Inline)
    @staticmethod
    def quality_selection(video_id: str) -> InlineKeyboardMarkup:
        """Quality selection with glassmorphism inline buttons"""
        buttons = [
            [
                InlineKeyboardButton(text="🎬 4K (2160p)", callback_data=f"qual_2160_{video_id}"),
                InlineKeyboardButton(text="🎥 Full HD (1080p)", callback_data=f"qual_1080_{video_id}"),
            ],
            [
                InlineKeyboardButton(text="📹 HD (720p)", callback_data=f"qual_720_{video_id}"),
                InlineKeyboardButton(text="📱 Mobile (480p)", callback_data=f"qual_480_{video_id}"),
            ],
            [
                InlineKeyboardButton(text="🎵 Audio Only (MP3)", callback_data=f"qual_audio_{video_id}"),
            ],
            [
                InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_download"),
            ],
            [
                InlineKeyboardButton(text="◀️ بازگشت", callback_data="back_prev"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Coin Menu
    @staticmethod
    def coin_menu() -> InlineKeyboardMarkup:
        """Coin management menu with glassmorphism design"""
        buttons = [
            [
                InlineKeyboardButton(text="💰 تاریخچه سکه ها", callback_data="coin_history"),
                InlineKeyboardButton(text="🔄 تبدیل سکه", callback_data="coin_convert"),
            ],
            [
                InlineKeyboardButton(text="👥 دعوت دوستان", callback_data="referral"),
                InlineKeyboardButton(text="🏆 رتبه بندی", callback_data="leaderboard"),
            ],
            [
                InlineKeyboardButton(text="◀️ بازگشت", callback_data="back_prev"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Settings Menu
    @staticmethod
    def settings_menu() -> InlineKeyboardMarkup:
        """Settings menu with glassmorphism design"""
        buttons = [
            [
                InlineKeyboardButton(text="🌐 زبان", callback_data="setting_language"),
                InlineKeyboardButton(text="🔔 اطلاعات", callback_data="setting_notifications"),
            ],
            [
                InlineKeyboardButton(text="🎨 تم", callback_data="setting_theme"),
                InlineKeyboardButton(text="🔒 امنیت", callback_data="setting_security"),
            ],
            [
                InlineKeyboardButton(text="📞 تماس با ما", callback_data="setting_contact"),
                InlineKeyboardButton(text="◀️ بازگشت", callback_data="back_prev"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Profile Menu
    @staticmethod
    def profile_menu() -> InlineKeyboardMarkup:
        """Profile menu with glassmorphism design"""
        buttons = [
            [
                InlineKeyboardButton(text="👤 پروفایل", callback_data="profile_view"),
                InlineKeyboardButton(text="💳 اشتراک", callback_data="profile_subscription"),
            ],
            [
                InlineKeyboardButton(text="📥 دانلودهای من", callback_data="profile_downloads"),
                InlineKeyboardButton(text="🏅 نشان ها", callback_data="profile_badges"),
            ],
            [
                InlineKeyboardButton(text="◀️ بازگشت", callback_data="back_prev"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Referral Menu
    @staticmethod
    def referral_menu(referral_code: str) -> InlineKeyboardMarkup:
        """Referral menu with share options"""
        buttons = [
            [
                InlineKeyboardButton(text="💬 تلگرام", callback_data=f"share_telegram_{referral_code}"),
                InlineKeyboardButton(text="📋 کپی لینک", callback_data=f"copy_link_{referral_code}"),
            ],
            [
                InlineKeyboardButton(text="📊 آمار", callback_data="referral_stats"),
                InlineKeyboardButton(text="◀️ بازگشت", callback_data="back_prev"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Admin Menu
    @staticmethod
    def admin_menu() -> InlineKeyboardMarkup:
        """Admin panel menu with glassmorphism design"""
        buttons = [
            [
                InlineKeyboardButton(text="📊 آمار", callback_data="admin_stats"),
                InlineKeyboardButton(text="👥 کاربران", callback_data="admin_users"),
            ],
            [
                InlineKeyboardButton(text="📢 ارسال پیام", callback_data="admin_broadcast"),
                InlineKeyboardButton(text="💰 جایزه سکه", callback_data="admin_bonus"),
            ],
            [
                InlineKeyboardButton(text="🔧 تنظیمات", callback_data="admin_settings"),
                InlineKeyboardButton(text="◀️ خروج", callback_data="admin_exit"),
            ],
            [
                InlineKeyboardButton(text="◀️ بازگشت", callback_data="back_prev"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Subscription Plans
    @staticmethod
    def subscription_plans() -> InlineKeyboardMarkup:
        """Beautiful subscription plan buttons"""
        buttons = [
            [
                InlineKeyboardButton(text="⭐ رایگان", callback_data="plan_free"),
                InlineKeyboardButton(text="💎 پریمیوم", callback_data="plan_premium"),
                InlineKeyboardButton(text="👑 VIP", callback_data="plan_vip"),
            ],
            [
                InlineKeyboardButton(text="◀️ بازگشت", callback_data="back_prev"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Language Selection
    @staticmethod
    def language_selection() -> InlineKeyboardMarkup:
        """Language selection with flags"""
        buttons = [
            [
                InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="lang_fa"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            ],
            [
                InlineKeyboardButton(text="🇨🇳 中文", callback_data="lang_zh"),
                InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang_ar"),
            ],
            [
                InlineKeyboardButton(text="◀️ بازگشت", callback_data="back_prev"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Confirmation Dialog
    @staticmethod
    def confirm_dialog(action_id: str, yes_text: str = "✅ تأیید", no_text: str = "❌ لغو") -> InlineKeyboardMarkup:
        """Beautiful confirmation dialog"""
        buttons = [
            [
                InlineKeyboardButton(text=yes_text, callback_data=f"confirm_{action_id}"),
                InlineKeyboardButton(text=no_text, callback_data=f"cancel_{action_id}"),
            ]
            ,
            [
                InlineKeyboardButton(text="◀️ بازگشت", callback_data="back_prev"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Error Dialog
    @staticmethod
    def error_dialog() -> InlineKeyboardMarkup:
        """Error dialog with retry option"""
        buttons = [
            [
                InlineKeyboardButton(text="🔄 دوباره تلاش کنید", callback_data="retry"),
                InlineKeyboardButton(text="◀️ بازگشت", callback_data="back_main"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Platform Selection
    @staticmethod
    def platform_selection() -> InlineKeyboardMarkup:
        """Download platform selection with beautiful buttons"""
        buttons = [
            [
                InlineKeyboardButton(text="🎥 YouTube", callback_data="platform_youtube"),
                InlineKeyboardButton(text="📷 Instagram", callback_data="platform_instagram"),
            ],
            [
                InlineKeyboardButton(text="🎵 TikTok", callback_data="platform_tiktok"),
                InlineKeyboardButton(text="𝕏 Twitter", callback_data="platform_twitter"),
            ],
            [
                InlineKeyboardButton(text="🔗 دیگر لینک ها", callback_data="platform_direct"),
            ],
            [
                InlineKeyboardButton(text="◀️ بازگشت", callback_data="back_prev"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Empty State (no buttons)
    @staticmethod
    def remove_keyboard() -> ReplyKeyboardMarkup:
        """Remove keyboard display"""
        return ReplyKeyboardMarkup(
            keyboard=[],
            resize_keyboard=True,
            remove_keyboard=True
        )
