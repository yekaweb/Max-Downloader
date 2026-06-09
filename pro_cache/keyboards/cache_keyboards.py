"""
Pro Cache Keyboards
کیبوردهای اینلاین برای سیستم کش
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from utils.formatters import format_file_size


class CacheKeyboards:
    """کلاس برای ساخت کیبوردهای مربوط به کش"""
    
    @staticmethod
    def create_cache_options_keyboard(
        cache_count: int, 
        url_hash: str
    ) -> InlineKeyboardMarkup:
        """
        ایجاد کیبورد اصلی برای نمایش گزینه‌های کش
        
        Args:
            cache_count: تعداد کیفیت‌های موجود در کش
            url_hash: هش URL برای استفاده در callback
        
        Returns:
            InlineKeyboardMarkup با سه دکمه
        """
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            # دکمه اول: نمایش کیفیت‌های موجود
            [
                InlineKeyboardButton(
                    text=f"📚 {cache_count} کیفیت موجود در آرشیو (دریافت سریع)",
                    callback_data=f"show_cached:{url_hash}"
                )
            ],
            # دکمه دوم: جستجوی کیفیت‌های جدید
            [
                InlineKeyboardButton(
                    text="🔄 پیدا کردن کیفیت‌های جدید",
                    callback_data=f"download_new:{url_hash}"
                )
            ],
            # دکمه سوم: بازگشت
            [
                InlineKeyboardButton(
                    text="🔙 بازگشت",
                    callback_data="back_to_main"
                )
            ]
        ])
        
        return keyboard
    
    @staticmethod
    def create_qualities_keyboard(qualities: List) -> InlineKeyboardMarkup:
        """
        ایجاد کیبورد برای نمایش لیست کیفیت‌ها
        
        Args:
            qualities: لیست کیفیت‌های موجود
        
        Returns:
            InlineKeyboardMarkup با دکمه‌های کیفیت
        """
        keyboard_buttons = []
        
        # گروه‌بندی کیفیت‌ها بر اساس نوع
        video_qualities = []
        audio_qualities = []
        
        for quality in qualities:
            if quality.mime_type and 'audio' in quality.mime_type:
                audio_qualities.append(quality)
            else:
                video_qualities.append(quality)
        
        # اضافه کردن کیفیت‌های ویدیو
        if video_qualities:
            # سورت بر اساس resolution (از بالا به پایین)
            video_qualities.sort(
                key=lambda q: int(q.resolution.split('x')[1] if q.resolution and 'x' in q.resolution else '0'),
                reverse=True
            )
            
            for quality in video_qualities:
                quality_text = CacheKeyboards._format_quality_button(quality)
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=quality_text,
                        callback_data=f"send_cached:{quality.id}"
                    )
                ])
        
        # خط جدا کننده بین ویدیو و صدا
        if video_qualities and audio_qualities:
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text="━━━ فایل‌های صوتی ━━━",
                    callback_data="separator"
                )
            ])
        
        # اضافه کردن کیفیت‌های صوتی
        if audio_qualities:
            # سورت بر اساس bitrate (از بالا به پایین)
            audio_qualities.sort(
                key=lambda q: q.bitrate if q.bitrate else 0,
                reverse=True
            )
            
            for quality in audio_qualities:
                quality_text = CacheKeyboards._format_quality_button(quality, is_audio=True)
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=quality_text,
                        callback_data=f"send_cached:{quality.id}"
                    )
                ])
        
        # دکمه بازگشت
        keyboard_buttons.append([
            InlineKeyboardButton(
                text="◀️ بازگشت به گزینه‌ها",
                callback_data="back_to_options"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    @staticmethod
    def _format_quality_button(quality, is_audio: bool = False) -> str:
        """
        فرمت کردن متن دکمه کیفیت
        
        Args:
            quality: آبجکت کیفیت
            is_audio: آیا فایل صوتی است
        
        Returns:
            متن فرمت شده برای دکمه
        """
        if is_audio:
            # فرمت برای فایل صوتی
            icon = "🎵"
            if quality.bitrate:
                label = f"{quality.bitrate}kbps"
            else:
                label = quality.quality_label
            
            text = f"{icon} {label}"
        else:
            # فرمت برای فایل ویدیویی
            icon = "🎬"
            text = f"{icon} {quality.quality_label}"
            
            # اضافه کردن codec اگر موجود بود
            if quality.video_codec:
                codec_emoji = CacheKeyboards._get_codec_emoji(quality.video_codec)
                text += f" {codec_emoji}"
        
        # اضافه کردن حجم فایل
        if quality.file_size:
            size_text = format_file_size(quality.file_size)
            text += f" • {size_text}"
        
        # اضافه کردن فرمت فایل
        if quality.extension:
            text += f" • {quality.extension.upper()}"
        
        return text
    
    @staticmethod
    def _get_codec_emoji(codec: str) -> str:
        """دریافت emoji مناسب برای codec"""
        codec_emojis = {
            'h264': '📹',
            'h265': '🎥',
            'vp9': '🎞',
            'av1': '🎯',
            'aac': '🔊',
            'opus': '🎧',
            'mp3': '🎼'
        }
        
        codec_lower = codec.lower()
        for key, emoji in codec_emojis.items():
            if key in codec_lower:
                return emoji
        
        return '📽'  # پیش‌فرض
    
    @staticmethod
    def create_download_options_keyboard() -> InlineKeyboardMarkup:
        """کیبورد برای انتخاب نوع دانلود (ویدیو/صدا)"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎬 دانلود ویدیو",
                    callback_data="download_type:video"
                ),
                InlineKeyboardButton(
                    text="🎵 دانلود صدا",
                    callback_data="download_type:audio"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 بازگشت",
                    callback_data="back_to_main"
                )
            ]
        ])
        
        return keyboard
    
    @staticmethod
    def create_confirmation_keyboard() -> InlineKeyboardMarkup:
        """کیبورد تایید عملیات"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ تایید",
                    callback_data="confirm_action"
                ),
                InlineKeyboardButton(
                    text="❌ انصراف",
                    callback_data="cancel_action"
                )
            ]
        ])
        
        return keyboard
    
    @staticmethod
    def create_error_keyboard() -> InlineKeyboardMarkup:
        """کیبورد برای نمایش در هنگام خطا"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 تلاش مجدد",
                    callback_data="retry_action"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬 پشتیبانی",
                    url="https://t.me/support"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 منوی اصلی",
                    callback_data="main_menu"
                )
            ]
        ])
        
        return keyboard
    
    @staticmethod
    def create_loading_keyboard() -> InlineKeyboardMarkup:
        """کیبورد برای نمایش در حین بارگذاری"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏳ در حال پردازش...",
                    callback_data="loading"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ لغو عملیات",
                    callback_data="cancel_loading"
                )
            ]
        ])
        
        return keyboard