"""
Pro Cache Telegram Handlers
هندلرهای اصلی برای مدیریت کش در ربات تلگرام
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import List, Optional
import logging

from services.hash_service import HashService
from services.lookup_service import CacheLookupService
from services.storage_service import CacheStorageService
from database.repository import CacheRepository
from keyboards.cache_keyboards import CacheKeyboards
from utils.formatters import format_file_size, format_duration

# تنظیم logger
logger = logging.getLogger(__name__)

# ایجاد router
router = Router(name="cache_router")


class CacheStates(StatesGroup):
    """حالت‌های FSM برای فرآیند کش"""
    waiting_for_url = State()
    showing_cached_options = State()
    selecting_quality = State()
    downloading_new = State()


class CacheHandler:
    """کلاس اصلی برای مدیریت هندلرهای کش"""
    
    def __init__(self):
        self.hash_service = HashService()
        self.lookup_service = CacheLookupService()
        self.storage_service = CacheStorageService()
        self.keyboards = CacheKeyboards()
    
    async def handle_url_message(self, message: Message, state: FSMContext):
        """
        پردازش URL ارسالی توسط کاربر
        """
        try:
            # استخراج و اعتبارسنجی URL
            url = message.text.strip()
            
            # بررسی اینکه URL معتبر است
            if not self._is_valid_url(url):
                await message.reply(
                    "❌ لطفاً یک لینک معتبر ارسال کنید.\n"
                    "پلتفرم‌های پشتیبانی شده:\n"
                    "• YouTube\n"
                    "• Instagram\n"
                    "• TikTok\n"
                    "• Twitter/X"
                )
                return
            
            # نمایش پیام در حال پردازش
            processing_msg = await message.reply("🔍 در حال بررسی لینک...")
            
            # تولید hash و دریافت اطلاعات URL
            url_info = self.hash_service.get_url_info(url)
            url_hash = url_info['hash']
            platform = url_info['platform']
            
            # ذخیره اطلاعات در state
            await state.update_data(
                url=url,
                url_hash=url_hash,
                platform=platform,
                url_info=url_info
            )
            
            # جستجو در کش
            cached_content = await self.lookup_service.find_cached_content(url_hash)
            
            if cached_content and cached_content.qualities:
                # محتوا در کش موجود است
                await self._show_cached_options(
                    message, 
                    processing_msg,
                    cached_content, 
                    url_hash,
                    state
                )
            else:
                # محتوا در کش نیست، شروع دانلود جدید
                await processing_msg.edit_text(
                    "🆕 این محتوا برای اولین بار درخواست شده است.\n"
                    "⏳ در حال دریافت اطلاعات از سرور..."
                )
                await self._start_fresh_download(message, url, state)
                
        except Exception as e:
            logger.error(f"Error handling URL: {e}")
            await message.reply(
                "❌ خطایی در پردازش لینک رخ داد.\n"
                "لطفاً دوباره تلاش کنید."
            )
    
    async def _show_cached_options(
        self, 
        message: Message,
        processing_msg: Message,
        cached_content,
        url_hash: str,
        state: FSMContext
    ):
        """نمایش گزینه‌های موجود در کش"""
        
        # تعداد کیفیت‌های موجود
        quality_count = len(cached_content.qualities)
        
        # ایجاد متن پیام
        text = (
            f"✅ این محتوا قبلاً دانلود شده است!\n\n"
            f"📹 **عنوان**: {cached_content.title}\n"
            f"⏱ **مدت زمان**: {format_duration(cached_content.duration)}\n"
            f"📅 **آخرین دسترسی**: {cached_content.last_accessed.strftime('%Y/%m/%d')}\n"
            f"🔢 **تعداد دسترسی**: {cached_content.access_count}\n\n"
            f"🎯 چه کاری انجام دهم؟"
        )
        
        # ایجاد keyboard
        keyboard = self.keyboards.create_cache_options_keyboard(
            quality_count,
            url_hash
        )
        
        # ویرایش پیام قبلی
        await processing_msg.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        # تنظیم state
        await state.set_state(CacheStates.showing_cached_options)
        await state.update_data(cached_content_id=cached_content.id)
    
    async def handle_show_cached_callback(
        self, 
        callback: CallbackQuery, 
        state: FSMContext
    ):
        """نمایش لیست کیفیت‌های کش شده"""
        
        # استخراج url_hash از callback data
        url_hash = callback.data.split(':')[1]
        
        # دریافت کیفیت‌ها
        qualities = await self.lookup_service.get_cached_qualities(url_hash)
        
        if not qualities:
            await callback.answer("❌ کیفیت‌های کش شده یافت نشد.", show_alert=True)
            return
        
        # ساخت keyboard برای کیفیت‌ها
        keyboard = self.keyboards.create_qualities_keyboard(qualities)
        
        # ایجاد متن
        text = "📋 **کیفیت‌های موجود در کش**:\n\n"
        
        for i, quality in enumerate(qualities, 1):
            text += (
                f"{i}. **{quality.quality_label}**\n"
                f"   📦 حجم: {format_file_size(quality.file_size)}\n"
                f"   📊 فرمت: {quality.extension.upper()}\n"
                f"   📥 دانلود شده: {quality.download_count} بار\n\n"
            )
        
        text += "🎯 یک کیفیت را انتخاب کنید:"
        
        # ویرایش پیام
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        await state.set_state(CacheStates.selecting_quality)
        await callback.answer()
    
    async def handle_send_cached_file(
        self, 
        callback: CallbackQuery,
        state: FSMContext,
        bot
    ):
        """ارسال فایل کش شده به کاربر"""
        
        # استخراج quality_id
        quality_id = int(callback.data.split(':')[1])
        
        # نمایش پیام در حال ارسال
        await callback.answer("⏳ در حال ارسال فایل...")
        
        try:
            # دریافت اطلاعات کیفیت
            quality = await self.lookup_service.get_quality_by_id(quality_id)
            
            if not quality:
                await callback.answer("❌ فایل یافت نشد.", show_alert=True)
                return
            
            # دریافت اطلاعات کامل محتوا
            cached_content = await self.lookup_service.get_cached_by_id(quality.cache_id)
            
            # ساخت caption
            caption = self._create_file_caption(cached_content, quality)
            
            # ارسال فایل با استفاده از file_id
            if quality.mime_type and quality.mime_type.startswith('video'):
                # ارسال به عنوان ویدیو
                await bot.send_video(
                    chat_id=callback.from_user.id,
                    video=quality.telegram_file_id,
                    caption=caption,
                    parse_mode="Markdown"
                )
            elif quality.mime_type and quality.mime_type.startswith('audio'):
                # ارسال به عنوان صدا
                await bot.send_audio(
                    chat_id=callback.from_user.id,
                    audio=quality.telegram_file_id,
                    caption=caption,
                    parse_mode="Markdown"
                )
            else:
                # ارسال به عنوان فایل
                await bot.send_document(
                    chat_id=callback.from_user.id,
                    document=quality.telegram_file_id,
                    caption=caption,
                    parse_mode="Markdown"
                )
            
            # بروزرسانی آمار
            await self.lookup_service.update_access_stats(quality_id)
            
            # پاک کردن پیام قبلی
            await callback.message.delete()
            
            # نمایش پیام موفقیت
            success_msg = await bot.send_message(
                chat_id=callback.from_user.id,
                text=(
                    "✅ **فایل با موفقیت ارسال شد!**\n\n"
                    "⚡ این فایل از حافظه کش ارسال شد.\n"
                    f"⏱ زمان پردازش: کمتر از 1 ثانیه\n"
                    f"💾 صرفه‌جویی در مصرف: {format_file_size(quality.file_size)}"
                ),
                parse_mode="Markdown"
            )
            
            # حذف state
            await state.clear()
            
        except Exception as e:
            logger.error(f"Error sending cached file: {e}")
            
            # احتمالاً file_id منقضی شده
            if "FILE_ID_INVALID" in str(e):
                await self._handle_expired_file_id(callback, quality_id, state)
            else:
                await callback.answer(
                    "❌ خطایی در ارسال فایل رخ داد.",
                    show_alert=True
                )
    
    async def handle_download_new_callback(
        self,
        callback: CallbackQuery,
        state: FSMContext
    ):
        """شروع فرآیند دانلود جدید"""
        
        # دریافت اطلاعات از state
        data = await state.get_data()
        url = data.get('url')
        
        if not url:
            await callback.answer("❌ URL یافت نشد.", show_alert=True)
            return
        
        await callback.message.edit_text(
            "🔄 **جستجوی کیفیت‌های جدید**\n\n"
            "⏳ در حال دریافت اطلاعات از سرور اصلی...\n"
            "این فرآیند ممکن است کمی زمان ببرد."
        )
        
        # شروع دانلود جدید
        await self._start_fresh_download(callback.message, url, state)
        await callback.answer()
    
    async def handle_back_callback(
        self,
        callback: CallbackQuery,
        state: FSMContext
    ):
        """بازگشت به منوی اصلی"""
        
        await callback.message.delete()
        await state.clear()
        
        await callback.message.answer(
            "🔙 به منوی اصلی بازگشتید.\n\n"
            "💡 برای دانلود محتوای جدید، لینک مورد نظر را ارسال کنید."
        )
        await callback.answer()
    
    def _is_valid_url(self, url: str) -> bool:
        """بررسی معتبر بودن URL"""
        # بررسی ساده برای URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # بررسی وجود دامنه
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return url_pattern.match(url) is not None
    
    def _create_file_caption(self, cached_content, quality) -> str:
        """ساخت caption برای فایل ارسالی"""
        caption = (
            f"📹 **{cached_content.title}**\n\n"
            f"🎯 کیفیت: {quality.quality_label}\n"
            f"📦 حجم: {format_file_size(quality.file_size)}\n"
            f"📊 فرمت: {quality.extension.upper()}\n"
        )
        
        if cached_content.duration:
            caption += f"⏱ مدت زمان: {format_duration(cached_content.duration)}\n"
        
        if cached_content.uploader:
            caption += f"👤 منتشرکننده: {cached_content.uploader}\n"
        
        caption += (
            f"\n⚡ **ارسال سریع از کش**\n"
            f"💾 صرفه‌جویی در زمان و حجم مصرفی"
        )
        
        return caption
    
    async def _start_fresh_download(
        self,
        message: Message,
        url: str,
        state: FSMContext
    ):
        """شروع فرآیند دانلود جدید"""
        # این متد باید به ماژول دانلود اصلی متصل شود
        # فعلاً فقط یک پیام نمایش می‌دهیم
        
        await message.edit_text(
            "🆕 **شروع دانلود جدید**\n\n"
            "⏳ در حال دریافت اطلاعات...\n"
            "📡 اتصال به سرور...\n\n"
            "لطفاً صبر کنید..."
        )
        
        # TODO: اتصال به download module
        # result = await download_module.process(url)
        # await self.storage_service.store_to_cache(result)
        
        await state.set_state(CacheStates.downloading_new)
    
    async def _handle_expired_file_id(
        self,
        callback: CallbackQuery,
        quality_id: int,
        state: FSMContext
    ):
        """مدیریت file_id منقضی شده"""
        
        await callback.message.edit_text(
            "⚠️ **فایل کش منقضی شده است**\n\n"
            "فایل‌های ذخیره شده در تلگرام پس از مدتی منقضی می‌شوند.\n"
            "در حال دانلود مجدد این فایل...\n\n"
            "⏳ لطفاً صبر کنید..."
        )
        
        # علامت‌گذاری کش به عنوان نامعتبر
        await self.storage_service.mark_cache_invalid(quality_id)
        
        # شروع دانلود مجدد
        data = await state.get_data()
        url = data.get('url')
        if url:
            await self._start_fresh_download(callback.message, url, state)


# ثبت هندلرها در router
cache_handler = CacheHandler()

# هندلر برای دریافت URL
@router.message(F.text & ~F.text.startswith('/'))
async def url_message_handler(message: Message, state: FSMContext):
    await cache_handler.handle_url_message(message, state)

# هندلر برای نمایش کیفیت‌های کش شده
@router.callback_query(F.data.startswith('show_cached:'))
async def show_cached_callback(callback: CallbackQuery, state: FSMContext):
    await cache_handler.handle_show_cached_callback(callback, state)

# هندلر برای ارسال فایل کش شده
@router.callback_query(F.data.startswith('send_cached:'))
async def send_cached_callback(callback: CallbackQuery, state: FSMContext, bot):
    await cache_handler.handle_send_cached_file(callback, state, bot)

# هندلر برای دانلود جدید
@router.callback_query(F.data.startswith('download_new:'))
async def download_new_callback(callback: CallbackQuery, state: FSMContext):
    await cache_handler.handle_download_new_callback(callback, state)

# هندلر برای بازگشت
@router.callback_query(F.data == 'back_to_main')
async def back_callback(callback: CallbackQuery, state: FSMContext):
    await cache_handler.handle_back_callback(callback, state)