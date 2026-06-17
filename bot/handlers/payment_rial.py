"""ZarinPal (Iranian Rial) payment gateway integration"""

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from services import SubscriptionService
from database.models import Payment, Plan
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("pay_rial"))
async def cmd_pay_rial(message: Message, state: FSMContext, session: AsyncSession):
    """
    /pay_rial command - Start Rial payment flow
    
    Payment in Iranian Rial via ZarinPal gateway
    
    Usage:
    /pay_rial - Interactive plan selection in Rial
    /pay_rial premium 3 - Direct payment for premium 3 months
    """
    
    try:
        args = message.text.split()
        
        if len(args) == 1:
            # Interactive mode - show plans in Rial
            await show_rial_payment_plans(message, state, session)
        elif len(args) >= 3:
            # Direct mode: /pay_rial <plan> <months>
            plan_name = args[1]
            months = int(args[2])
            
            if months < 1 or months > 12:
                await message.reply("❌ ماه باید بین 1 تا 12 باشد")
                return
            
            await process_rial_payment_request(
                message, state, session,
                plan_name=plan_name,
                months=months
            )
        else:
            await message.reply(
                "❌ فرمت غلط است.\n"
                "استفاده:\n"
                "/pay_rial - انتخاب پلن\n"
                "/pay_rial premium 3 - پرداخت premium برای 3 ماه"
            )
    except ValueError:
        await message.reply("❌ مقدار ماه اشتباه است")
    except Exception as e:
        logger.error(f"Error in pay_rial command: {e}")
        await message.reply("❌ خطا رخ داد")


async def show_rial_payment_plans(
    message: Message,
    state: FSMContext,
    session: AsyncSession
):
    """Show available payment plans in Iranian Rial"""
    try:
        from database.models import Plan
        
        # Get all plans
        result = await session.execute(select(Plan))
        plans = result.scalars().all()
        
        if not plans:
            await message.reply("❌ پلنی موجود نیست")
            return
        
        # Create payment options keyboard (Rial pricing)
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
        
        for plan in plans:
            if plan.name.lower() != "free":
                # Convert to Rial (approximate: 1 USD = 42000 Rial)
                rial_price = int(plan.price * 42000)
                keyboard.inline_keyboard.append([
                    types.InlineKeyboardButton(
                        text=f"💳 {plan.name} - {rial_price:,} ریال/ماه",
                        callback_data=f"pay_rial_plan_{plan.id}"
                    )
                ])
        
        await message.reply(
            "💰 <b>انتخاب پلن اشتراک:</b>\n\n"
            "پلن‌های موجود با پرداخت ریالی",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error showing Rial payment plans: {e}")
        await message.reply("❌ خطا رخ داد")


async def process_rial_payment_request(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    plan_name: str,
    months: int
):
    """Process Rial payment request - create ZarinPal invoice"""
    try:
        from database.models import Plan
        
        # Get plan by name
        result = await session.execute(
            select(Plan).where(Plan.name.ilike(plan_name))
        )
        plan = result.scalars().first()
        
        if not plan:
            await message.reply(f"❌ پلن '{plan_name}' یافت نشد")
            return
        
        # Calculate total amount in Rial
        rial_price = int(plan.price * 42000)
        total_rial = rial_price * months
        
        # Create payment record (pending)
        try:
            payment = Payment(
                user_id=message.from_user.id,
                plan_id=plan.id,
                amount=total_rial,
                currency="IRR",  # Iranian Rial
                status="pending",
                months=months,
                payment_method="zarinpal",
                created_at=datetime.utcnow()
            )
            session.add(payment)
            await session.commit()
            payment_id = payment.id
        except Exception as e:
            logger.error(f"Error creating Rial payment record: {e}")
            await message.reply("❌ خطا در ایجاد پرداخت")
            return
        
        # Create invoice via ZarinPal (placeholder - requires API)
        # In production, integrate with zarinpal-py library
        
        # ZarinPal payment gateway implementation:
        # from zarinpal_py import Client
        # client = Client(merchant_id="YOUR_MERCHANT_ID", sandbox=False)
        # result = client.payment_request(
        #     amount=total_rial,
        #     description=f"DLBot {plan.name} subscription",
        #     email=user.email,
        #     mobile=user.phone
        # )
        # if result['Status'] == 100:
        #     payment_url = f"https://www.zarinpal.com/pg/StartPay/{result['Authority']}"
        
        payment_url = f"https://zarinpal.example.com/invoice/{payment_id}"
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton(
                text="💳 پرداخت با ریال ایرانی",
                url=payment_url
            )
        ]])
        
        message_text = (
            f"💰 <b>صورت حساب پرداخت</b>\n\n"
            f"پلن: {plan.name}\n"
            f"مدت: {months} ماه\n"
            f"قیمت ماهانه: {rial_price:,} ریال\n"
            f"<b>مجموع: {total_rial:,} ریال</b>\n\n"
            f"✅ برای پرداخت با رمز ارز کلیک کنید"
        )
        
        await message.reply(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error processing Rial payment: {e}")
        await message.reply("❌ خطا رخ داد")


async def handle_rial_payment_callback(
    user_id: int,
    payment_id: int,
    authority: str,
    status: str,
    session: AsyncSession,
    bot
):
    """
    Handle ZarinPal payment callback
    
    Called when payment is received via ZarinPal
    """
    try:
        from database.models import Payment
        
        # Get payment record
        payment = await session.get(Payment, payment_id)
        if not payment:
            logger.error(f"Payment {payment_id} not found")
            return False
        
        if status == "OK":  # ZarinPal success code
            # Verify payment with ZarinPal
            # from zarinpal_py import Client
            # client = Client(merchant_id="YOUR_MERCHANT_ID", sandbox=False)
            # result = client.payment_verify(
            #     amount=int(payment.amount),
            #     authority=authority
            # )
            # if result['Status'] == 100:
            #     payment verified successfully
            
            # Update payment status
            payment.status = "completed"
            payment.completed_at = datetime.utcnow()
            payment.payment_reference = authority  # Store ZarinPal authority
            
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
                # Notify user in Persian
                try:
                    await bot.send_message(
                        chat_id=payment.user_id,
                        text=f"✅ <b>پرداخت موفق!</b>\n\n"
                             f"اشتراک شما برای {payment.months} ماه فعال شد\n"
                             f"از ویژگی‌های Premium لذت ببرید! 🎉",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify user {payment.user_id}: {e}")
            
            await session.commit()
            return True
        
        elif status == "FAILED":
            payment.status = "failed"
            await session.commit()
            
            try:
                await bot.send_message(
                    chat_id=payment.user_id,
                    text="❌ پرداخت ناموفق\n\nلطفاً دوباره امتحان کنید",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to notify user {payment.user_id}: {e}")
            
            return False
        
        return False
        
    except Exception as e:
        logger.error(f"Error handling Rial payment callback: {e}")
        return False


@router.callback_query(F.data.startswith("pay_rial_plan_"))
async def handle_rial_plan_selection(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession
):
    """Handle Rial plan selection from callback"""
    try:
        plan_id = int(query.data.split("_")[-1])
        
        # Get plan
        from database.models import Plan
        plan = await session.get(Plan, plan_id)
        
        if not plan:
            await query.answer("❌ پلن یافت نشد", show_alert=True)
            return
        
        # Store in FSM
        await state.update_data(plan_id=plan_id, plan_name=plan.name)
        
        # Ask for months
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(
                text=f"{i} ماه",
                callback_data=f"pay_rial_months_{i}"
            )] for i in range(1, 13)
        ])
        
        rial_price = int(plan.price * 42000)
        
        await query.message.edit_text(
            f"📝 <b>انتخاب مدت زمان</b>\n\n"
            f"پلن: {plan.name}\n"
            f"قیمت: {rial_price:,} ریال/ماه\n\n"
            f"چند ماه می‌خواهید؟",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        try:
            await query.answer()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error: {e}")
        await query.answer("خطا رخ داد", show_alert=True)


@router.callback_query(F.data.startswith("pay_rial_months_"))
async def handle_rial_months_selection(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession
):
    """Handle Rial months selection"""
    try:
        months = int(query.data.split("_")[-1])
        
        data = await state.get_data()
        plan_name = data.get("plan_name", "Unknown")
        
        await process_rial_payment_request(
            query.message, state, session,
            plan_name=plan_name,
            months=months
        )
        
        try:
            await query.answer()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error: {e}")
        await query.answer("خطا رخ داد", show_alert=True)


__all__ = ["router", "handle_rial_payment_callback"]
