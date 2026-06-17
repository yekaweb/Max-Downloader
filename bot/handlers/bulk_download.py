"""
PHASE 2: Bulk/Parallel Download Handler
مرحله 2.4 - اضافه کردن گزینه دانلود چندگانه
"""

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from bot.states.download import DownloadStates
from services.parallel_download_service import get_coordinator, DownloadCoordinator
from utils.progress_tracker import ProgressTracker, ProgressUpdater
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

router = Router()


# ============================================
# Bulk Download Options
# ============================================

@router.callback_query(F.data == "bulk_download_option")
async def show_bulk_download_menu(query: types.CallbackQuery, state: FSMContext):
    """
    نمایش منوی دانلود چندگانه
    """
    try:
        await query.answer()
    except Exception:
        pass
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📥 دانلود چندگانه (تا 10 لینک)",
                callback_data="start_bulk_download"
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
        "🎯 **گزینه‌های دانلود:**\n\n"
        "📥 **دانلود چندگانه**: تا 3 دانلود همزمان\n"
        "💡 هر دانلود ~2 دقیقه\n"
        "⚡ تمام دانلود‌ها موازی انجام می‌شوند",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "start_bulk_download")
async def start_bulk_download(query: types.CallbackQuery, state: FSMContext):
    """
    شروع حالت دریافت چندین لینک
    """
    try:
        await query.answer()
    except Exception:
        pass
    await query.message.edit_text(
        "📥 **دانلود چندگانه**\n\n"
        "لطفاً چند لینک را ارسال کنید (هر یکی در سطر جداگانه)\n\n"
        "**مثال:**\n"
        "https://youtube.com/watch?v=xyz\n"
        "https://youtube.com/watch?v=abc\n"
        "https://youtube.com/watch?v=def\n\n"
        "حداکثر 10 لینک\n"
        "حداکثر 3 دانلود همزمان"
    )
    
    await state.set_state(DownloadStates.waiting_bulk_urls)


@router.message(DownloadStates.waiting_bulk_urls)
async def handle_bulk_urls(
    message: Message,
    state: FSMContext,
    session: AsyncSession
):
    """
    دریافت و پردازش چندین لینک
    """
    text = message.text.strip()
    
    # تقسیم‌کردن لینک‌ها
    urls = [url.strip() for url in text.split("\n") if url.strip().startswith("http")]
    
    if not urls:
        await message.reply("❌ لطفاً حداقل یک لینک معتبر ارسال کنید")
        return
    
    if len(urls) > 10:
        await message.reply("❌ حداکثر 10 لینک مجاز است")
        return
    
    # ارسال پیام شروع
    status_msg = await message.answer(
        f"⏳ **درحال آماده‌سازی {len(urls)} دانلود...**\n\n"
        f"لطفاً منتظر بمانید..."
    )
    
    try:
        # گرفتن coordinator
        coordinator = await get_coordinator()
        
        # افزودن هر لینک به صف
        positions = []
        for idx, url in enumerate(urls, 1):
            result = await coordinator.add_download(
                user_id=message.from_user.id,
                url=url,
                chat_id=message.chat.id,
                priority=1
            )
            positions.append(result)
            logger.info(f"[BULK] Added download #{idx}: {url[:60]} at position {result['position']}")
        
        # نمایش تأیید
        queue_stats = await coordinator.get_queue_stats()
        confirmation = (
            f"✅ **{len(urls)} دانلود اضافه شد**\n\n"
            f"📋 **موقعیت‌های در صف:**\n"
        )
        
        for idx, (url, pos) in enumerate(zip(urls, positions), 1):
            confirmation += f"   #{idx}: {url[:40]}... → صفحه #{pos['position']}\n"
        
        confirmation += (
            f"\n📊 **وضعیت صف:**\n"
            f"   فعال: {queue_stats['active_downloads']}\n"
            f"   در صف: {queue_stats['queue_length']}\n"
            f"   دسترسی‌پذیر: {queue_stats['available_slots']}\n\n"
            f"⏱️ زمان انتظار برآورد: {queue_stats['queue_length'] * 2} دقیقه"
        )
        
        await status_msg.edit_text(confirmation)
        
        # ذخیره در state برای reference
        await state.update_data(
            bulk_urls=urls,
            bulk_positions=positions,
            status_message_id=status_msg.message_id
        )
        
        await state.set_state(DownloadStates.monitoring_bulk_downloads)
        
    except Exception as e:
        logger.error(f"[BULK] Error: {e}")
        await status_msg.edit_text(f"❌ خطا: {e}")


# ============================================
# Monitoring Bulk Downloads
# ============================================

@router.callback_query(F.data == "check_bulk_status")
async def check_bulk_status(query: types.CallbackQuery, state: FSMContext):
    """
    بررسی وضعیت دانلود‌های چندگانه
    """
    try:
        await query.answer()
    except Exception:
        pass
    
    try:
        coordinator = await get_coordinator()
        
        # بررسی دانلود‌های کاربر
        user_downloads = await coordinator.get_user_downloads(query.from_user.id)
        active_downloads = await coordinator.manager.get_active_downloads()
        queue_stats = await coordinator.get_queue_stats()
        
        # تولید پیام وضعیت
        status_msg = await ProgressTracker.generate_queue_status(queue_stats)
        
        if user_downloads:
            status_msg += f"\n\n👤 **دانلود‌های شما:**\n"
            for download in user_downloads:
                status_msg += f"   • {download['url'][:40]}...\n"
                status_msg += f"     وضعیت: {download['status']}\n"
        
        await query.message.edit_text(status_msg)
        
    except Exception as e:
        logger.error(f"[BULK STATUS] Error: {e}")
        await query.message.edit_text(f"❌ خطا: {e}")


# ============================================
# Queue Monitoring Task (Background)
# ============================================

async def start_queue_processor():
    """
    شروع پردازشگر صف (باید در startup اجرا شود)
    """
    try:
        coordinator = await get_coordinator()
        logger.info("[QUEUE] Starting queue processor")
        
        # اجرای processor
        await coordinator.process_queue()
        
    except Exception as e:
        logger.error(f"[QUEUE] Processor error: {e}")


async def monitor_downloads():
    """
    مانیتور‌کردن دانلود‌های فعال (برای نوتیفیکیشن‌های تناوبی)
    """
    try:
        coordinator = await get_coordinator()
        
        while True:
            active = await coordinator.manager.get_active_downloads()
            
            if active:
                logger.info(f"[MONITOR] Active downloads: {len(active)}")
                
                # اینجا می‌توانید callback‌های progress اضافه کنید
                for url, info in active.items():
                    logger.debug(f"[MONITOR] {info['current']}/{info['total']}: {info['progress']:.0f}%")
            
            await asyncio.sleep(5)
    
    except Exception as e:
        logger.error(f"[MONITOR] Error: {e}")


# ============================================
# Helper Functions
# ============================================

async def get_bulk_download_keyboard() -> InlineKeyboardMarkup:
    """
    کلیدبورد برای دانلود چندگانه
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📥 شروع دانلود چندگانه",
                callback_data="start_bulk_download"
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 وضعیت صف",
                callback_data="check_bulk_status"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ لغو",
                callback_data="cancel_bulk_download"
            )
        ]
    ])


async def send_bulk_options(message: Message):
    """
    ارسال گزینه‌های دانلود چندگانه
    """
    keyboard = await get_bulk_download_keyboard()
    
    await message.answer(
        "🎯 **دانلود چندگانه**\n\n"
        "می‌توانید تا 10 لینک را به صورت همزمان دانلود کنید\n"
        "حداکثر 3 دانلود در هر لحظه انجام می‌شود\n\n"
        "⚡ هر دانلود ~2 دقیقه\n"
        "💾 تمام فایل‌ها در کش ذخیره می‌شوند",
        reply_markup=keyboard
    )


__all__ = [
    'router',
    'start_queue_processor',
    'monitor_downloads',
    'get_bulk_download_keyboard',
    'send_bulk_options'
]
