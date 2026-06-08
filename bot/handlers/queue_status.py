"""
🔴 Phase 5: Queue Status Handlers
Purpose: User-facing queue status and management commands

Features:
- Real-time queue status display
- User position tracking
- Estimated wait time
- Task management (pause, cancel, retry)
- Resource status monitoring
"""

import logging
from typing import Optional

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import datetime

from services.queue_service import (
    get_queue_manager,
    get_resource_manager,
    get_orchestrator,
    Priority
)

logger = logging.getLogger(__name__)

router = Router(name="queue_status")


# ============================================================================
# QUEUE STATUS DISPLAY HANDLERS
# ============================================================================

async def check_queue_status(query: CallbackQuery) -> bool:
    """
    نمایش وضعیت فعلی صف
    
    Args:
        query: Callback query از کاربر
        
    Returns:
        bool: True اگر موفق
    """
    try:
        queue_manager = get_queue_manager()
        resource_manager = get_resource_manager()
        
        # گرفتن آمار
        queue_stats = await queue_manager.get_queue_stats()
        resource_status = await resource_manager.get_resource_status()
        user_tasks = await queue_manager.get_user_tasks(query.from_user.id)
        
        # تعداد tasks کاربر در صف
        queued_count = len([t for t in user_tasks if t.get('status') == 'queued'])
        active_count = len([t for t in user_tasks if t.get('status') == 'processing'])
        
        # ساخت پیام
        message_text = (
            "📋 <b>وضعیت صف دانلود‌ها</b>\n\n"
        )
        
        # وضعیت صف
        message_text += (
            f"🔴 <b>صف دانلودها:</b>\n"
            f"  • در صف: {queue_stats['queue_length']}\n"
            f"  • درحال پردازش: {queue_stats['active_tasks']}/{queue_stats['max_concurrent']}\n"
            f"  • تکمیل شده: {queue_stats['completed_tasks']}\n"
            f"  • زمان انتظار برآورد: {queue_stats['estimated_wait_minutes']} دقیقه\n\n"
        )
        
        # وضعیت منابع
        message_text += (
            f"💻 <b>وضعیت منابع سیستم:</b>\n"
            f"  • CPU: {resource_status['cpu_percent']}%\n"
            f"  • RAM: {resource_status['memory_percent']}%\n"
            f"  • Disk: {resource_status['disk_percent']}%\n"
            f"  • وضعیت: {'🟢 سالم' if resource_status['status'] == 'healthy' else '🔴 پر بار'}\n\n"
        )
        
        # tasks کاربر
        if active_count > 0:
            message_text += f"⚙️ <b>Tasks شما:</b>\n"
            message_text += f"  • درحال پردازش: {active_count}\n"
            message_text += f"  • در صف: {queued_count}\n\n"
        
        message_text += (
            "💡 <b>نکات:</b>\n"
            "• هرچه priority بالاتر، سریع‌تر پردازش می‌شود\n"
            "• Premium users عموماً زودتر پردازش می‌شوند\n"
            "• منابع سیستم بر سرعت تأثیر می‌گذارد\n"
        )
        
        # کلید‌های اختیاری
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="check_queue_status"),
                InlineKeyboardButton(text="❌ بستن", callback_data="close_queue_status")
            ]
        ])
        
        await query.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        logger.info(f"[PHASE 5] Queue status shown to user {query.from_user.id}")
        return True
        
    except Exception as e:
        logger.error(f"[PHASE 5] Error showing queue status: {e}")
        await query.answer(f"❌ خطا: {str(e)}", show_alert=True)
        return False


async def show_my_tasks(query: CallbackQuery) -> bool:
    """
    نمایش tasks کاربر
    
    Args:
        query: Callback query
        
    Returns:
        bool: موفق یا نه
    """
    try:
        queue_manager = get_queue_manager()
        user_tasks = await queue_manager.get_user_tasks(query.from_user.id)
        
        if not user_tasks:
            await query.answer("❌ هیچ task ندارید", show_alert=True)
            return False
        
        message_text = "📋 <b>Tasks شما:</b>\n\n"
        
        # دسته‌بندی tasks
        active = [t for t in user_tasks if t.get('status') == 'processing']
        queued = [t for t in user_tasks if t.get('status') == 'queued']
        completed = [t for t in user_tasks if t.get('status') == 'completed']
        failed = [t for t in user_tasks if t.get('status') == 'failed']
        
        if active:
            message_text += "⚙️ <b>درحال پردازش:</b>\n"
            for task in active:
                progress = task.get('progress', 0)
                url = task.get('url', 'N/A')
                message_text += (
                    f"  • {url[:50]}...\n"
                    f"    Progress: {progress}%\n"
                )
        
        if queued:
            message_text += "\n⏳ <b>در صف:</b>\n"
            for i, task in enumerate(queued, 1):
                url = task.get('url', 'N/A')
                message_text += f"  {i}. {url[:50]}...\n"
        
        if completed:
            message_text += f"\n✅ <b>تکمیل شده ({len(completed)}):</b>\n"
        
        if failed:
            message_text += f"\n❌ <b>ناموفق ({len(failed)}):</b>\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="show_my_tasks"),
            ],
            [
                InlineKeyboardButton(text="❌ بستن", callback_data="close_queue_status")
            ]
        ])
        
        await query.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"[PHASE 5] Error showing user tasks: {e}")
        await query.answer(f"❌ خطا: {str(e)}", show_alert=True)
        return False


async def show_resource_status(query: CallbackQuery) -> bool:
    """
    نمایش وضعیت کامل منابع
    
    Args:
        query: Callback query
        
    Returns:
        bool: موفق یا نه
    """
    try:
        resource_manager = get_resource_manager()
        status = await resource_manager.get_resource_status()
        
        # تعریف status emoji
        cpu_emoji = "🟢" if status['cpu_percent'] < 50 else "🟡" if status['cpu_percent'] < 80 else "🔴"
        mem_emoji = "🟢" if status['memory_percent'] < 50 else "🟡" if status['memory_percent'] < 80 else "🔴"
        disk_emoji = "🟢" if status['disk_percent'] < 50 else "🟡" if status['disk_percent'] < 80 else "🔴"
        
        message_text = (
            "💻 <b>وضعیت منابع سیستم</b>\n\n"
            f"{cpu_emoji} <b>CPU:</b> {status['cpu_percent']}%\n"
            f"{mem_emoji} <b>RAM:</b> {status['memory_percent']}%\n"
            f"{disk_emoji} <b>Disk:</b> {status['disk_percent']}%\n\n"
            f"📊 <b>وضعیت کلی:</b> {'🟢 سالم' if status['status'] == 'healthy' else '🔴 پر بار'}\n"
            f"💡 <b>توصیه:</b> {status['recommendation']}\n\n"
            f"<i>آپدیت شد: {datetime.utcnow().strftime('%H:%M:%S')}</i>"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="show_resource_status"),
                InlineKeyboardButton(text="❌ بستن", callback_data="close_queue_status")
            ]
        ])
        
        await query.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"[PHASE 5] Error showing resource status: {e}")
        await query.answer(f"❌ خطا: {str(e)}", show_alert=True)
        return False


# ============================================================================
# QUEUE MANAGEMENT HANDLERS
# ============================================================================

async def show_queue_menu(message: Message, state: FSMContext) -> bool:
    """
    نمایش منوی صف
    
    Args:
        message: پیام کاربر
        state: FSM state
        
    Returns:
        bool: موفق یا نه
    """
    try:
        message_text = (
            "🔴 <b>سیستم صف دانلودها</b>\n\n"
            "ما از سیستم صف اولویت‌دار استفاده می‌کنیم تا:\n"
            "✅ دانلودها سریع‌تر شود\n"
            "✅ منابع بهتر مدیریت شود\n"
            "✅ کاربران Premium اول تکمیل شوند\n\n"
            "موارد زیر را انتخاب کنید:"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 وضعیت صف", callback_data="check_queue_status"),
                InlineKeyboardButton(text="⚙️ Tasks من", callback_data="show_my_tasks")
            ],
            [
                InlineKeyboardButton(text="💻 منابع سیستم", callback_data="show_resource_status"),
            ],
            [
                InlineKeyboardButton(text="❌ بستن", callback_data="close_queue_status")
            ]
        ])
        
        await message.answer(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        logger.info(f"[PHASE 5] Queue menu shown to user {message.from_user.id}")
        return True
        
    except Exception as e:
        logger.error(f"[PHASE 5] Error showing queue menu: {e}")
        await message.answer(f"❌ خطا: {str(e)}")
        return False


async def close_queue_status(query: CallbackQuery) -> bool:
    """
    بستن منوی صف
    
    Args:
        query: Callback query
        
    Returns:
        bool: موفق یا نه
    """
    try:
        await query.message.delete()
        await query.answer("❌ منو بسته شد")
        logger.info(f"[PHASE 5] Queue menu closed for user {query.from_user.id}")
        return True
    except Exception as e:
        logger.error(f"[PHASE 5] Error closing queue menu: {e}")
        return False


# ============================================================================
# CALLBACK QUERY HANDLERS
# ============================================================================

@router.callback_query(F.data == "check_queue_status")
async def handle_check_queue(query: CallbackQuery):
    """هندلر برای بررسی وضعیت صف"""
    await check_queue_status(query)


@router.callback_query(F.data == "show_my_tasks")
async def handle_show_tasks(query: CallbackQuery):
    """هندلر برای نمایش tasks کاربر"""
    await show_my_tasks(query)


@router.callback_query(F.data == "show_resource_status")
async def handle_show_resources(query: CallbackQuery):
    """هندلر برای نمایش وضعیت منابع"""
    await show_resource_status(query)


@router.callback_query(F.data == "close_queue_status")
async def handle_close_queue(query: CallbackQuery):
    """هندلر برای بستن منوی صف"""
    await close_queue_status(query)


# ============================================================================
# COMMAND HANDLERS
# ============================================================================

@router.message(F.text == "/queue")
async def cmd_queue_status(message: Message, state: FSMContext):
    """
    دستور /queue برای نمایش صف
    
    استفاده:
        /queue - نمایش منوی صف
    """
    await show_queue_menu(message, state)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'router',
    'check_queue_status',
    'show_my_tasks',
    'show_resource_status',
    'show_queue_menu',
    'close_queue_status',
]
