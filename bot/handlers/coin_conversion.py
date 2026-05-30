"""Coin conversion handler - allow users to convert coins to subscription credits"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.repositories import UserRepository
from database.connection import AsyncSessionLocal
from database.models import Subscription, Plan
from services import CoinTransactionService, SubscriptionService
from sqlalchemy import select
from datetime import datetime, timedelta

router = Router()

# Conversion rate: 100 coins = 1 month of subscription
COINS_PER_MONTH = 100.0


@router.message(Command("convert_coins"))
async def start_coin_conversion(message: Message):
    """Start coin to subscription conversion process"""
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        
        if not user:
            await message.reply("❌ User not found")
            return
        
        if user.total_coins < COINS_PER_MONTH:
            await message.reply(
                f"❌ Insufficient coins!\n\n"
                f"You have: {user.total_coins:.0f} coins\n"
                f"Need: {COINS_PER_MONTH:.0f} coins for 1 month Premium\n\n"
                f"💡 Invite friends using your referral code to earn more coins!"
            )
            return
        
        # Get available plans
        result = await session.execute(select(Plan).where(Plan.is_active == True))
        plans = result.scalars().all()
        
        conversion_text = f"""
💳 **Convert Coins to Subscription**

💎 **Your Balance**: {user.total_coins:.0f} coins
📊 **Conversion Rate**: {COINS_PER_MONTH:.0f} coins = 1 month

**Available Plans:**
"""
        
        keyboard_buttons = []
        for plan in plans:
            months = 1
            coins_needed = COINS_PER_MONTH * months
            affordable = user.total_coins >= coins_needed
            
            emoji = "✅" if affordable else "❌"
            button_text = f"{emoji} {plan.name} ({coins_needed:.0f} coins)"
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"convert_plan_{plan.id}_{months}" if affordable else "convert_unavailable"
                )
            ])
            
            conversion_text += f"\n• {plan.name}: {coins_needed:.0f} coins"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await message.reply(conversion_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data.startswith("convert_plan_"))
async def confirm_conversion(query: CallbackQuery):
    """Confirm coin to subscription conversion"""
    try:
        _, plan_id, months = query.data.split("_")
        plan_id = int(plan_id)
        months = int(months)
        
        async with AsyncSessionLocal() as session:
            user_repo = UserRepository(session)
            user = await user_repo.get_by_telegram_id(query.from_user.id)
            
            if not user:
                await query.answer("❌ User not found", show_alert=True)
                return
            
            # Get plan
            result = await session.execute(select(Plan).where(Plan.id == plan_id))
            plan = result.scalars().first()
            
            if not plan:
                await query.answer("❌ Plan not found", show_alert=True)
                return
            
            coins_needed = COINS_PER_MONTH * months
            
            if user.total_coins < coins_needed:
                await query.answer(
                    f"❌ Insufficient coins! Need {coins_needed:.0f}, have {user.total_coins:.0f}",
                    show_alert=True
                )
                return
            
            # Deduct coins
            coin_service = CoinTransactionService(session)
            success, msg, tx = await coin_service.spend_coins(
                user_id=user.id,
                amount=coins_needed,
                description=f"Converted to {plan.name} subscription ({months} month{'s' if months > 1 else ''})"
            )
            
            if not success:
                await query.answer(f"❌ {msg}", show_alert=True)
                return
            
            # Create subscription
            now = datetime.now()
            end_date = now + timedelta(days=30 * months)
            
            subscription = Subscription(
                user_id=user.id,
                plan_id=plan_id,
                start_date=now,
                end_date=end_date,
                is_active=True,
                auto_renew=False
            )
            session.add(subscription)
            await session.commit()
            
            confirmation_text = f"""
✅ **Subscription Converted Successfully!**

📦 **Plan**: {plan.name}
⏱️ **Duration**: {months} month{'s' if months > 1 else ''}
💎 **Cost**: {coins_needed:.0f} coins
📅 **Valid Until**: {end_date.strftime('%Y-%m-%d')}

🎉 Your subscription is now active!
"""
            
            await query.message.edit_text(confirmation_text, parse_mode="Markdown")
            await query.answer("✅ Subscription activated!", show_alert=False)
            
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


@router.callback_query(F.data == "convert_unavailable")
async def conversion_unavailable(query: CallbackQuery):
    """Handle unavailable conversion"""
    await query.answer(
        "❌ You don't have enough coins for this plan",
        show_alert=True
    )


__all__ = ["router"]
