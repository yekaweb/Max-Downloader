"""
PHASE 3: Stream Upload Handler Integration
مرحله 3.3 - ادغام با handlers ربات
"""

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from bot.states.download import DownloadStates
from services.hybrid_download_upload import get_hybrid_service
from services.stream_upload_service import StreamUploadService, BufferManager
from utils.progress_tracker import ProgressTracker
import logging
import asyncio

logger = logging.getLogger(__name__)

router = Router()


# ============================================
# Stream Upload Options
# ============================================

@router.callback_query(F.data == "stream_upload_option")
async def show_stream_upload_menu(query: types.CallbackQuery, state: FSMContext):
    """
    نمایش منوی آپلود جریانی
    """
    await query.answer()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📤 آپلود جریانی (فایل‌های بزرگ)",
                callback_data="enable_stream_upload"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 بازگشت",
                callback_data="back_to_main"
            )
        ]
    ])
    
    await query.message.edit_text(
        "📤 **آپلود جریانی (Stream Upload)**\n\n"
        "🚀 **ویژگی‌ها:**\n"
        "⚡ 50% سریع‌تر برای فایل‌های بزرگ\n"
        "📉 مصرف حافظه 40% کم‌تر\n"
        "📊 آپلود chunks (5MB)\n"
        "🔄 Parallel D/U\n\n"
        "آیا می‌خواهید stream upload فعال کنید؟",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "enable_stream_upload")
async def enable_stream_upload(query: types.CallbackQuery, state: FSMContext):
    """
    فعال‌کردن آپلود جریانی برای دانلود‌های آینده
    """
    await query.answer()
    
    # ذخیره در state
    await state.update_data(use_stream_upload=True)
    
    await query.message.edit_text(
        "✅ **آپلود جریانی فعال شد**\n\n"
        "تمام دانلود‌های بعدی با این روش انجام خواهند شد:\n\n"
        "1️⃣ دانلود chunks (5MB)\n"
        "2️⃣ آپلود موازی\n"
        "3️⃣ مصرف حافظه کم\n\n"
        "🚀 آماده برای دانلود!"
    )


# ============================================
# Stream Upload Integration
# ============================================

async def apply_stream_upload(
    file_path: str,
    chat_id: int,
    bot,
    message: Message,
    use_hybrid: bool = False
) -> bool:
    """
    استفاده از stream upload برای آپلود فایل
    
    Args:
        file_path: مسیر فایل
        chat_id: Chat ID
        bot: Telegram bot
        message: Telegram message
        use_hybrid: استفاده از hybrid (D/U موازی)
    
    Returns:
        True اگر موفق
    """
    try:
        # ایجاد status message
        status_msg = await message.answer(
            "📤 **درحال آپلود جریانی...**\n\n"
            "🔄 آپلود chunks...\n"
            "⏳ لطفاً منتظر بمانید"
        )
        
        if use_hybrid:
            # Hybrid: دانلود + آپلود موازی
            logger.info(f"[STREAM] Using hybrid mode for: {file_path}")
            
            hybrid_service = await get_hybrid_service()
            
            # تابع برای آپدیت progress
            async def update_progress(progress_info):
                """آپدیت پیشرفت آپلود"""
                progress = progress_info.get('progress', 0)
                uploaded = progress_info.get('uploaded_mb', 0)
                total = progress_info.get('total_mb', 0)
                speed = progress_info.get('speed', 0)
                
                progress_bar = ProgressTracker.generate_progress_bar(int(progress), 100, 15)
                
                text = (
                    f"📤 **آپلود جریانی**\n\n"
                    f"{progress_bar} {progress:.0f}%\n"
                    f"📊 {uploaded:.1f}MB / {total:.1f}MB\n"
                    f"⚡ {speed:.1f} MB/s"
                )
                
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=status_msg.message_id,
                        text=text
                    )
                except:
                    pass  # اگر edit نشد، ادامه بده
            
            # آپلود جریانی
            upload_result = await hybrid_service.download_compress_upload_parallel(
                file_path,
                chat_id,
                bot,
                progress_callback=update_progress
            )
            
            if upload_result['status'] == 'success':
                duration = upload_result.get('duration', 0)
                
                await status_msg.edit_text(
                    f"✅ **آپلود موفق**\n\n"
                    f"⏱️ زمان: {duration:.1f}s\n"
                    f"📤 روش: Stream Upload (Hybrid)\n"
                    f"💾 فایل آماده است!"
                )
                return True
            else:
                error = upload_result.get('error', 'نامشخص')
                await status_msg.edit_text(f"❌ خطا: {error}")
                return False
        
        else:
            # Stream Upload: آپلود عادی با chunks
            logger.info(f"[STREAM] Using stream upload for: {file_path}")
            
            upload_service = StreamUploadService()
            
            # تابع برای آپدیت progress
            async def update_stream_progress(progress_info):
                """آپدیت پیشرفت"""
                progress = progress_info.get('progress', 0)
                uploaded = progress_info.get('uploaded_mb', 0)
                total = progress_info.get('total_mb', 0)
                speed = progress_info.get('speed', 0)
                
                progress_bar = ProgressTracker.generate_progress_bar(int(progress), 100, 15)
                
                text = (
                    f"📤 **آپلود جریانی**\n\n"
                    f"{progress_bar} {progress:.0f}%\n"
                    f"📊 {uploaded:.1f}MB / {total:.1f}MB\n"
                    f"⚡ {speed:.1f} MB/s"
                )
                
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=status_msg.message_id,
                        text=text
                    )
                except:
                    pass
            
            # آپلود
            result = await upload_service.stream_upload_to_telegram(
                file_path,
                chat_id,
                bot,
                progress_callback=update_stream_progress
            )
            
            if result['status'] == 'success':
                file_size_mb = result.get('file_size', 0) / (1024 * 1024)
                
                await status_msg.edit_text(
                    f"✅ **آپلود موفق**\n\n"
                    f"📤 روش: Stream Upload\n"
                    f"📦 حجم: {file_size_mb:.1f}MB\n"
                    f"💾 فایل آماده است!"
                )
                return True
            else:
                error = result.get('error', 'نامشخص')
                await status_msg.edit_text(f"❌ خطا: {error}")
                return False
    
    except Exception as e:
        logger.error(f"[STREAM] Error: {e}")
        await message.answer(f"❌ خطا در آپلود: {e}")
        return False


# ============================================
# Buffer Status Monitoring
# ============================================

@router.callback_query(F.data == "check_stream_status")
async def check_stream_status(query: types.CallbackQuery):
    """
    بررسی وضعیت stream upload و بفر
    """
    await query.answer()
    
    try:
        hybrid_service = await get_hybrid_service()
        
        buffer_status = await hybrid_service.get_buffer_status()
        active_tasks = await hybrid_service.get_all_hybrid_tasks()
        
        # تولید پیام وضعیت
        status_text = (
            f"📤 **وضعیت Stream Upload**\n\n"
            f"**بفر (Buffer):**\n"
            f"   {buffer_status['current_mb']:.1f}MB / {buffer_status['max_mb']:.1f}MB\n"
            f"   استفاده: {buffer_status['usage_percent']:.0f}%\n"
            f"   وضعیت: {buffer_status['status']}\n\n"
            f"**فعال:**\n"
            f"   Chunks: {buffer_status['chunks_in_buffer']}\n"
            f"   Hybrid Tasks: {len(active_tasks)}\n"
        )
        
        await query.message.edit_text(status_text)
    
    except Exception as e:
        logger.error(f"[STREAM] Status check error: {e}")
        await query.message.edit_text(f"❌ خطا: {e}")


__all__ = [
    'router',
    'apply_stream_upload'
]
