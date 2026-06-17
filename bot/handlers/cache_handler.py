"""
Cache-aware download handler
Integrate caching with FSM download flow
"""

import os
import asyncio
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from bot.states.download import DownloadStates
from bot.keyboards.inline.cached_files import (
    get_cached_files_keyboard,
    get_cache_action_keyboard,
    get_cache_format_options_keyboard,
)
from utils.cache_handler import CacheManager, format_cached_list_message
from utils.file_cleanup import FileCleanup
from utils.format_sizes import get_exact_format_sizes
from database.models.cached_download import CachedDownload

router = Router()


@router.callback_query(F.data.startswith("send_cached:"))
async def send_cached(query: CallbackQuery, state: FSMContext, db_session: AsyncSession):
    """Send a cached file to the user using telegram file_id."""
    await query.answer("⏳ در حال ارسال فایل کش‌شده...")
    try:
        cache_id = int(query.data.split(":", 1)[1])
    except (ValueError, IndexError):
        await query.answer("❌ داده نامعتبر", show_alert=True)
        return

    cached = await db_session.get(CachedDownload, cache_id)
    if not cached or not cached.telegram_file_id:
        await query.answer("❌ فایل کش‌شده یافت نشد", show_alert=True)
        return

    caption = (
        f"✅ {cached.media_title[:50]}\n"
        f"💾 {cached.file_size / (1024*1024):.1f} MB"
    )

    try:
        if "video" in (cached.file_type or "").lower():
            await query.message.answer_video(
                cached.telegram_file_id,
                caption=caption,
            )
        else:
            await query.message.answer_document(
                cached.telegram_file_id,
                caption=caption,
            )

        cache_manager = CacheManager(db_session)
        await cache_manager.increment_usage_count(cache_id)
        await query.answer("✅ فایل ارسال شد")

    except Exception as exc:
        logger.error(f"Error sending cached file: {exc}")
        await query.answer("❌ خطا در ارسال فایل کش‌شده", show_alert=True)


@router.callback_query(F.data == "fresh_download_search")
async def fresh_download_search(query: CallbackQuery, state: FSMContext):
    """Switch from cache flow to fresh download flow."""
    try:
        await query.answer()
    except Exception:
        pass
    await query.message.answer(
        "🔄 در حال آماده‌سازی دانلود تازه. لطفاً لینک جدید یا همان لینک موجود را ارسال کنید."
    )
    await state.clear()



async def check_and_show_cache(
    user_id: int,
    source_url: str,
    message: Message,
    state: FSMContext,
    db_session,
) -> bool:
    """
    Check if URL has cached downloads
    If yes: show cached files and return True
    If no: return False (proceed to normal flow)
    """
    try:
        cache_manager = CacheManager(db_session)
        cached = await cache_manager.find_cached_downloads(source_url)
        
        if not cached:
            # No cache found
            return False
        
        # Cache found - show to user
        cache_text = format_cached_list_message(cached)
        
        # Store cache list in session for later reference
        session_data = await state.get_data()
        session_data["cached_downloads"] = cached
        await state.update_data(session_data)
        
        # Show cache with interactive buttons
        await message.answer(
            cache_text,
            reply_markup=get_cached_files_keyboard(cached)
        )
        
        await state.set_state(DownloadStates.selecting_cached_file)
        return True
        
    except Exception as e:
        logger.error(f"Error checking cache: {e}")
        return False


async def handle_cached_file_selection(
    query: CallbackQuery,
    state: FSMContext,
    db_session,
):
    """Handle user selecting a cached file"""
    try:
        # Extract cache ID from callback
        cache_id = int(query.data.split(":")[1])
        
        cache_manager = CacheManager(db_session)
        
        # Get cached download details
        from database.models.cached_download import CachedDownload
        cached = db_session.query(CachedDownload).filter(
            CachedDownload.id == cache_id
        ).first()
        
        if not cached:
            await query.answer("❌ فایل کش‌شده پیدا نشد", show_alert=True)
            return
        
        # Store in session
        session_data = await state.get_data()
        session_data["selected_cached_file"] = {
            "id": cached.id,
            "telegram_file_id": cached.telegram_file_id,
            "title": cached.media_title,
            "quality": cached.quality,
            "size_mb": cached.file_size_mb,
        }
        await state.update_data(session_data)
        
        # Show action menu
        message_text = f"""
✅ **فایل انتخاب شد**

📺 نام: {cached.media_title[:60]}
📊 کیفیت: {cached.quality}
💾 حجم: {cached.file_size_mb:.2f} MB
🎬 نوع: {cached.file_type}

اکنون می‌توانید:
1. **✅ دانلود** - فایل کش‌شده را ارسال کنید
2. **🔄 فرمت دیگر** - کیفیت یا فرمت جدیدی دانلود کنید
3. **❌ حذف** - این کش را حذف کنید
"""
        
        await query.message.edit_text(
            message_text,
            reply_markup=get_cache_action_keyboard()
        )
        
        await state.set_state(DownloadStates.selecting_format_type)
        
    except Exception as e:
        logger.error(f"Error handling cached file selection: {e}")
        await query.answer(f"❌ خطا: {str(e)}", show_alert=True)


async def deliver_cached_file(
    query: CallbackQuery,
    state: FSMContext,
    bot,
    db_session,
):
    """
    Deliver cached file to user using stored telegram_file_id
    
    Much faster than re-downloading - just forward the file from cache
    """
    try:
        session_data = await state.get_data()
        cached_file = session_data.get("selected_cached_file")
        
        if not cached_file:
            await query.answer("❌ فایل انتخاب‌شده ای پیدا نشد", show_alert=True)
            return
        
        telegram_file_id = cached_file.get("telegram_file_id")
        file_size_mb = cached_file.get("size_mb")
        
        # Show progress message
        progress_msg = await query.message.answer(
            f"⬆️ **درحال ارسال فایل کش‌شده...**\n\n"
            f"📺 {cached_file.get('title', '')[:50]}\n"
            f"💾 {file_size_mb:.2f} MB"
        )
        
        # Send file using cached file_id
        try:
            if file_size_mb < 50:  # For smaller files, assume video
                sent_message = await bot.send_video(
                    chat_id=query.from_user.id,
                    video=telegram_file_id,
                    caption=f"✅ {cached_file.get('title', '')[:50]}\n💾 {file_size_mb:.2f} MB"
                )
            else:  # For larger files, send as document
                sent_message = await bot.send_document(
                    chat_id=query.from_user.id,
                    document=telegram_file_id,
                    caption=f"✅ {cached_file.get('title', '')[:50]}\n💾 {file_size_mb:.2f} MB"
                )
            
            # Update usage count
            cache_manager = CacheManager(db_session)
            await cache_manager.increment_usage_count(cached_file.get("id"))
            
            # Delete progress message
            await progress_msg.delete()
            
            # Success message
            await query.message.answer(
                f"✅ **فایل ارسال شد!**\n\n"
                f"💡 فایل از حافظه‌ی نهان بازیابی شد (دانلود دوباره نشد)"
            )
            
            await query.answer("✅ موفق!", show_alert=False)
            
        except Exception as send_error:
            logger.error(f"Error sending cached file: {send_error}")
            await query.answer(f"❌ خطا در ارسال: {str(send_error)}", show_alert=True)
            await progress_msg.delete()
        
        # Clear session
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error delivering cached file: {e}")
        await query.answer(f"❌ خطا: {str(e)}", show_alert=True)


async def cleanup_and_save_cache(
    file_path: str,
    telegram_file_id: str,
    source_url: str,
    source_platform: str,
    media_info: dict,
    quality: str,
    format_codec: str,
    format_container: str,
    db_session,
):
    """
    After successful upload to Telegram:
    1. Save telegram_file_id to cache
    2. Delete temp file
    """
    try:
        cache_manager = CacheManager(db_session)
        
        # Extract metadata
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        file_type = media_info.get("mime_type", "application/octet-stream")
        media_title = media_info.get("title", "Unknown")
        media_duration = media_info.get("duration", None)
        media_uploader = media_info.get("uploader", None)
        
        # Get resolution info
        resolution_width = media_info.get("width", None)
        resolution_height = media_info.get("height", None)
        
        # Save to cache
        await cache_manager.save_cached_download(
            source_url=source_url,
            source_platform=source_platform,
            media_title=media_title,
            telegram_file_id=telegram_file_id,
            file_size=file_size,
            file_type=file_type,
            quality=quality,
            format_codec=format_codec,
            format_container=format_container,
            resolution_width=resolution_width,
            resolution_height=resolution_height,
            media_duration=media_duration,
            media_uploader=media_uploader,
        )
        
        # Delete temp file (after short delay to ensure upload complete)
        cleanup_success = await FileCleanup.cleanup_after_upload(file_path, delay_seconds=5)
        
        if cleanup_success:
            logger.info(f"✅ Cleanup complete for: {media_title}")
        else:
            logger.warning(f"⚠️ Could not cleanup: {file_path}")
        
    except Exception as e:
        logger.error(f"Error in cleanup_and_save_cache: {e}")


__all__ = [
    "check_and_show_cache",
    "handle_cached_file_selection",
    "deliver_cached_file",
    "cleanup_and_save_cache",
]
