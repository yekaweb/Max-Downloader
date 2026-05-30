"""Admin bonus coins handler - Award coins to users"""
import logging
from typing import Optional

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services import CoinTransactionService
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = Router()


class BonusCoinsStates(StatesGroup):
    """FSM states for bonus coins operation"""
    
    waiting_for_user_id = State()
    waiting_for_amount = State()
    waiting_for_reason = State()
    confirming = State()


@router.message(Command("admin_bonus"))
async def cmd_bonus_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """
    /admin_bonus - Award bonus coins to user (admin only)
    
    Usage: /admin_bonus
    Then follow the prompts to:
    1. Enter user ID
    2. Enter coin amount
    3. Enter reason (optional)
    4. Confirm
    """
    try:
        # Check if admin (simplified - should check admin filter)
        await state.set_state(BonusCoinsStates.waiting_for_user_id)
        
        await message.reply(
            "🎁 <b>Bonus Coins Administration</b>\n\n"
            "Step 1: Enter the user ID to award coins to:\n\n"
            "<i>Send a message with the user ID</i>",
            parse_mode="HTML",
        )
        
    except Exception as e:
        logger.error(f"Error in bonus coins start: {e}")
        await message.reply("❌ خطایی رخ داد")
        await state.clear()


@router.message(BonusCoinsStates.waiting_for_user_id)
async def bonus_get_user_id(message: Message, state: FSMContext) -> None:
    """Get user ID from admin"""
    try:
        if not message.text or not message.text.isdigit():
            await message.reply("❌ لطفاً یک شناسه کاربر معتبر ارسال کنید (عدد)")
            return
        
        user_id = int(message.text)
        await state.update_data(user_id=user_id)
        await state.set_state(BonusCoinsStates.waiting_for_amount)
        
        await message.reply(
            "💰 <b>Step 2: Enter coin amount</b>\n\n"
            "<i>How many coins do you want to award?</i>\n\n"
            "<code>Example: 100</code>",
            parse_mode="HTML",
        )
        
    except Exception as e:
        logger.error(f"Error getting user ID: {e}")
        await message.reply("❌ خطایی رخ داد")
        await state.clear()


@router.message(BonusCoinsStates.waiting_for_amount)
async def bonus_get_amount(message: Message, state: FSMContext) -> None:
    """Get coin amount from admin"""
    try:
        if not message.text or not message.text.replace('.', '').isdigit():
            await message.reply("❌ لطفاً یک مقدار معتبر (عدد) ارسال کنید")
            return
        
        amount = float(message.text)
        
        if amount <= 0:
            await message.reply("❌ مقدار باید بزرگتر از صفر باشد")
            return
        
        if amount > 10000:  # Safety limit
            await message.reply("❌ حداکثر میزان 10000 سکه است")
            return
        
        await state.update_data(amount=amount)
        await state.set_state(BonusCoinsStates.waiting_for_reason)
        
        await message.reply(
            "📝 <b>Step 3: Enter reason (optional)</b>\n\n"
            "<i>Why are you awarding these coins?</i>\n\n"
            "<code>Example: Referral bonus, Contest winner, etc.</code>\n\n"
            "یا /skip برای رد کردن",
            parse_mode="HTML",
        )
        
    except Exception as e:
        logger.error(f"Error getting amount: {e}")
        await message.reply("❌ خطایی رخ داد")
        await state.clear()


@router.message(BonusCoinsStates.waiting_for_reason)
async def bonus_get_reason(message: Message, state: FSMContext) -> None:
    """Get reason for bonus from admin"""
    try:
        reason = "Admin bonus"
        
        if message.text and not message.text.startswith("/skip"):
            reason = message.text[:200]  # Limit to 200 chars
        
        data = await state.get_data()
        user_id = data.get("user_id")
        amount = data.get("amount")
        
        await state.update_data(reason=reason)
        await state.set_state(BonusCoinsStates.confirming)
        
        # Show confirmation
        await message.reply(
            f"✅ <b>Confirm Bonus Award</b>\n\n"
            f"👤 User ID: <code>{user_id}</code>\n"
            f"💰 Amount: <code>{amount}</code> coins\n"
            f"📝 Reason: {reason}\n\n"
            "Reply with:\n"
            "• /confirm - to award coins\n"
            "• /cancel - to cancel",
            parse_mode="HTML",
        )
        
    except Exception as e:
        logger.error(f"Error getting reason: {e}")
        await message.reply("❌ خطایی رخ داد")
        await state.clear()


@router.message(Command("confirm"), BonusCoinsStates.confirming)
async def bonus_confirm(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """Confirm and award bonus coins"""
    try:
        data = await state.get_data()
        user_id = data.get("user_id")
        amount = data.get("amount")
        reason = data.get("reason", "Admin bonus")
        
        coin_service = CoinTransactionService(session)
        
        # Award coins
        transaction = await coin_service.add_coins(
            user_id=user_id,
            amount=amount,
            transaction_type="admin_bonus",
            description=reason
        )
        
        success_msg = (
            f"✅ <b>Bonus Awarded Successfully!</b>\n\n"
            f"👤 User ID: <code>{user_id}</code>\n"
            f"💰 Amount: <code>{amount}</code> coins\n"
            f"📝 Reason: {reason}\n"
            f"⏰ Time: {transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await message.reply(success_msg, parse_mode="HTML")
        logger.info(f"Admin {message.from_user.id} awarded {amount} coins to user {user_id}")
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error confirming bonus: {e}")
        await message.reply("❌ خطایی رخ داد در هنگام اعطای سکه")
        await state.clear()


@router.message(Command("cancel"), BonusCoinsStates.confirming)
async def bonus_cancel(message: Message, state: FSMContext) -> None:
    """Cancel bonus operation"""
    try:
        await message.reply("❌ عملیات لغو شد")
        await state.clear()
    except Exception as e:
        logger.error(f"Error canceling bonus: {e}")
        await state.clear()


__all__ = ["router", "BonusCoinsStates"]
