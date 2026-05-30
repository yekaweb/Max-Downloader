"""CryptoBot payment integration - Telegram native crypto payments"""

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from services import SubscriptionService
from database.models import Payment, Plan
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("pay"))
async def cmd_pay(message: Message, state: FSMContext, session: AsyncSession):
    """
    /pay command - Start payment flow
    
    Usage:
    /pay - Interactive plan selection
    /pay premium 3 - Direct payment for premium 3 months
    """
    
    try:
        args = message.text.split()
        
        if len(args) == 1:
            # Interactive mode - show plans
            await show_payment_plans(message, state, session)
        elif len(args) >= 3:
            # Direct mode: /pay <plan> <months>
            plan_name = args[1]
            months = int(args[2])
            
            if months < 1 or months > 12:
                await message.reply("❌ Months must be between 1 and 12")
                return
            
            await process_payment_request(
                message, state, session,
                plan_name=plan_name,
                months=months
            )
        else:
            await message.reply(
                "❌ Invalid format.\n"
                "Usage:\n"
                "/pay - Select plan\n"
                "/pay premium 3 - Pay for premium 3 months"
            )
    except ValueError:
        await message.reply("❌ Invalid month value")
    except Exception as e:
        logger.error(f"Error in pay command: {e}")
        await message.reply("❌ An error occurred")


async def show_payment_plans(
    message: Message,
    state: FSMContext,
    session: AsyncSession
):
    """Show available payment plans"""
    try:
        from database.models import Plan
        from sqlalchemy import select
        
        # Get all plans
        result = await session.execute(select(Plan))
        plans = result.scalars().all()
        
        if not plans:
            await message.reply("❌ No payment plans available")
            return
        
        # Create payment options keyboard
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
        
        for plan in plans:
            if plan.name.lower() != "free":
                keyboard.inline_keyboard.append([
                    types.InlineKeyboardButton(
                        text=f"💳 {plan.name} - ${plan.price}/month",
                        callback_data=f"pay_plan_{plan.id}"
                    )
                ])
        
        await message.reply(
            "💰 <b>Select a subscription plan:</b>\n\n"
            "Available plans with cryptocurrency payment",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error showing payment plans: {e}")
        await message.reply("❌ An error occurred")


async def process_payment_request(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    plan_name: str,
    months: int
):
    """Process payment request - create invoice"""
    try:
        from database.models import Plan
        from sqlalchemy import select
        
        # Get plan by name
        result = await session.execute(
            select(Plan).where(Plan.name.ilike(plan_name))
        )
        plan = result.scalars().first()
        
        if not plan:
            await message.reply(f"❌ Plan '{plan_name}' not found")
            return
        
        # Calculate total amount
        total_amount = plan.price * months
        
        # Create payment record (pending)
        try:
            payment = Payment(
                user_id=message.from_user.id,
                plan_id=plan.id,
                amount=total_amount,
                currency="USD",
                status="pending",
                months=months,
                created_at=datetime.utcnow()
            )
            session.add(payment)
            await session.commit()
            payment_id = payment.id
        except Exception as e:
            logger.error(f"Error creating payment record: {e}")
            await message.reply("❌ Failed to create payment")
            return
        
        # Create invoice via CryptoBot (placeholder - requires API key)
        # In production, integrate with aiocryptopay
        invoice_url = f"https://cryptobot.example.com/invoice/{payment_id}"
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton(
                text="💳 Pay with Crypto",
                url=invoice_url
            )
        ]])
        
        message_text = (
            f"💰 <b>Payment Invoice</b>\n\n"
            f"Plan: {plan.name}\n"
            f"Duration: {months} months\n"
            f"Price per month: ${plan.price}\n"
            f"<b>Total: ${total_amount}</b>\n\n"
            f"✅ Click below to pay with cryptocurrency"
        )
        
        await message.reply(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error processing payment: {e}")
        await message.reply("❌ An error occurred")


async def handle_payment_callback(
    user_id: int,
    payment_id: int,
    status: str,
    session: AsyncSession,
    bot
):
    """
    Handle payment callback from CryptoBot
    
    Called when payment is received
    """
    try:
        from database.models import Payment
        
        # Get payment record
        payment = await session.get(Payment, payment_id)
        if not payment:
            logger.error(f"Payment {payment_id} not found")
            return False
        
        if status == "paid":
            # Update payment status
            payment.status = "completed"
            payment.completed_at = datetime.utcnow()
            
            # Create subscription
            sub_service = SubscriptionService(session)
            expires_at = datetime.utcnow() + timedelta(days=30 * payment.months)
            
            success, msg = await sub_service.create_subscription(
                user_id=payment.user_id,
                plan_id=payment.plan_id,
                expires_at=expires_at,
                payment_id=payment.id
            )
            
            if success:
                # Notify user
                try:
                    await bot.send_message(
                        chat_id=payment.user_id,
                        text=f"✅ <b>Payment Successful!</b>\n\n"
                             f"Your subscription is now active for {payment.months} months\n"
                             f"Enjoy premium features! 🎉",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify user {payment.user_id}: {e}")
            
            await session.commit()
            return True
        
        elif status == "failed":
            payment.status = "failed"
            await session.commit()
            
            try:
                await bot.send_message(
                    chat_id=payment.user_id,
                    text="❌ Payment Failed\n\nPlease try again",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to notify user {payment.user_id}: {e}")
            
            return False
        
        return False
        
    except Exception as e:
        logger.error(f"Error handling payment callback: {e}")
        return False


# Placeholder for CryptoBot webhook endpoint
# This would be registered in the FastAPI app

"""
@app.post("/api/payment/cryptobot/callback")
async def cryptobot_callback(payload: dict, session: AsyncSession = Depends(get_db)):
    '''Handle CryptoBot payment callback'''
    user_id = payload.get("user_id")
    payment_id = payload.get("invoice_id")
    status = payload.get("status")  # paid, failed, expired
    
    from bot.loader import bot
    success = await handle_payment_callback(
        user_id, payment_id, status, session, bot
    )
    
    return {"status": "ok" if success else "error"}
"""

__all__ = ["router", "handle_payment_callback", "show_payment_plans"]
