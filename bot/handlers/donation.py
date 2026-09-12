"""
Donation & VIP Passkey Account Pool Handler for DLBot.
Enables users to donate idle Gmail accounts in exchange for tiered VIP subscriptions:
  - 2 Accounts -> Sepahbod VIP (50 GB/day)
  - 3 Accounts -> Esfandiar VIP (100 GB/day)
  - 5 Accounts -> Rostam Lifetime VIP (Unlimited + AI Features)
"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.connection import AsyncSessionLocal
from services.account_pool_service import AccountPoolService

logger = logging.getLogger(__name__)
router = Router()


class DonationStates(StatesGroup):
    waiting_for_email = State()
    confirm_passkey = State()


def get_donation_main_keyboard() -> InlineKeyboardMarkup:
    """Main keyboard for donation center."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ اهدا و ثبت جیمیل جدید", callback_data="donate_add_email"),
                InlineKeyboardButton(text="📊 وضعیت حساب‌های من", callback_data="donate_my_status"),
            ],
            [
                InlineKeyboardButton(text="ℹ️ توضیحات امنیتی و Passkey", callback_data="donate_security_info"),
                InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="menu_main"),
            ]
        ]
    )


@router.message(Command("donate", "donate_account", "rostam"))
async def cmd_donate(message: Message, state: FSMContext):
    """Show Gmail Donation & VIP Tiers dashboard."""
    await state.clear()
    text = (
        "👑 **طرح اهدای جیمیل بیکار برای اشتراک VIP نامحدود**\n\n"
        "با اهدای جیمیل‌های بیکار خود، بدون پرداخت هزینه، اشتراک دائمی ربات را دریافت کنید:\n\n"
        "🎖️ **۲ ایمیل:** مقام **سپهبد** (۵۰ گیگ دانلود در روز + کیفیت 4K)\n"
        "⚔️ **۳ ایمیل:** مقام **اسفندیار** (۱۰۰ گیگ دانلود در روز + کیفیت 4K 60fps)\n"
        "👑 **۵ ایمیل:** مقام **رستم** (اشتراک همیشگی، سرعت فوق‌العاده و دوبله هوش مصنوعی)\n\n"
        "🔒 **امنیت و حریم خصوصی:**\n"
        "▫️ نیاز به ارسال رمز عبور نیست (فقط اتصال امن Passkey / Session Cookie).\n"
        "▫️ حساب‌ها فقط برای دور زدن محدودیت‌های ربات‌شناس یوتیوب استفاده می‌شوند.\n\n"
        "👇 برای شروع روی دکمه زیر کلیک کنید:"
    )
    await message.answer(text, reply_markup=get_donation_main_keyboard(), parse_mode="Markdown")


@router.callback_query(F.data == "donate_center")
async def cb_donate_center(callback: CallbackQuery, state: FSMContext):
    """Callback for donation center."""
    await state.clear()
    text = (
        "👑 **طرح اهدای جیمیل بیکار برای اشتراک VIP نامحدود**\n\n"
        "با اهدای جیمیل‌های بیکار خود، بدون پرداخت هزینه، اشتراک دائمی ربات را دریافت کنید:\n\n"
        "🎖️ **۲ ایمیل:** مقام **سپهبد** (۵۰ گیگ دانلود در روز + کیفیت 4K)\n"
        "⚔️ **۳ ایمیل:** مقام **اسفندیار** (۱۰۰ گیگ دانلود در روز + کیفیت 4K 60fps)\n"
        "👑 **۵ ایمیل:** مقام **رستم** (اشتراک همیشگی، سرعت فوق‌العاده و دوبله هوش مصنوعی)\n\n"
        "👇 یک گزینه را انتخاب کنید:"
    )
    await callback.message.edit_text(text, reply_markup=get_donation_main_keyboard(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "donate_add_email")
async def cb_donate_add(callback: CallbackQuery, state: FSMContext):
    """Prompt user to send their Gmail address."""
    await state.set_state(DonationStates.waiting_for_email)
    cancel_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ انصراف", callback_data="donate_center")]]
    )
    text = (
        "📧 **ثبت جیمیل اهدایی**\n\n"
        "لطفاً آدرس جیمیل خود را ارسال کنید (مثال: `example@gmail.com`):\n"
        "⚠️ توجه: از جیمیل‌های شخصی و حساس استفاده نکنید؛ ترجیحاً از جیمیل‌های فرعی استفاده فرمایید."
    )
    await callback.message.edit_text(text, reply_markup=cancel_kb, parse_mode="Markdown")
    await callback.answer()


@router.message(DonationStates.waiting_for_email)
async def process_donation_email(message: Message, state: FSMContext):
    """Validate and register donated Gmail."""
    email_text = message.text.strip().lower()
    
    if "@" not in email_text or not email_text.endswith(("@gmail.com", "@googlemail.com")):
        await message.answer("❌ ایمیل وارد شده معتبر نیست. لطفاً یک آدرس Gmail معتبر ارسال کنید:")
        return

    async with AsyncSessionLocal() as db:
        pool_svc = AccountPoolService(db)
        success, resp_msg, tier = await pool_svc.register_donation(
            telegram_id=message.from_user.id,
            email=email_text,
        )

    await state.clear()
    
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ اهدای ایمیل بعدی", callback_data="donate_add_email"),
                InlineKeyboardButton(text="📊 وضعیت من", callback_data="donate_my_status"),
            ],
            [InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="menu_main")]
        ]
    )

    await message.answer(resp_msg, reply_markup=kb, parse_mode="Markdown")


@router.callback_query(F.data == "donate_my_status")
async def cb_donate_status(callback: CallbackQuery):
    """View user's donated accounts and current VIP status."""
    async with AsyncSessionLocal() as db:
        pool_svc = AccountPoolService(db)
        status_info = await pool_svc.get_donor_status(callback.from_user.id)

    count = status_info["donations_count"]
    tier = status_info["tier"]
    accounts = status_info["accounts"]

    text = f"📊 **وضعیت حساب‌های اهدایی شما:**\n\n"
    text += f"▫️ تعداد کل حساب‌ها: **{count}**\n"
    
    if tier:
        text += f"▫️ سطح VIP فعال: **{tier['title']}**\n"
        text += f"▫️ سقف دانلود روزانه: **{tier['daily_limit_gb']} گیگابایت**\n"
        text += f"▫️ حداکثر کیفیت: **{tier['max_quality']}**\n\n"
    else:
        text += f"▫️ سطح VIP: **عادی** (با اهدای حداقل ۲ ایمیل فعال می‌شود)\n\n"

    if accounts:
        text += "📋 **لیست ایمیل‌های ثبت‌شده:**\n"
        for idx, acc in enumerate(accounts, 1):
            text += f"{idx}. `{acc['email']}` | وضعیت: {acc['status']} (دانلودها: {acc['used']})\n"
    else:
        text += "هنوز ایمیلی ثبت نکرده‌اید."

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ ثبت ایمیل جدید", callback_data="donate_add_email")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="donate_center")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "donate_security_info")
async def cb_security_info(callback: CallbackQuery):
    """Display transparency and security details of the Passkey donation."""
    text = (
        "🔐 **شفافیت و امنیت سیستم اهدای جیمیل:**\n\n"
        "1️⃣ **چرا به جیمیل نیاز است؟**\n"
        "یوتیوب روی آی‌پی دیتاسنترها محدودیت شدید اعمال می‌کند. با استفاده از کوکی‌های سشن حساب‌های واقعی، ربات بدون خطا ویدیوها را با بالاترین سرعت دریافت می‌کند.\n\n"
        "2️⃣ **امنیت چگونه حفظ می‌شود؟**\n"
        "▫️ نیاز به پسورد شما نیست.\n"
        "▫️ ربات به اطلاعات شخصی و ایمیل‌های شما دسترسی ندارد.\n"
        "▫️ مرورگر Headless فقط در یوتیوب سشن را فعال نگه می‌دارد.\n\n"
        "3️⃣ **توصیه ما:**\n"
        "همیشه از یک اکانت بدون استفاده یا جدید برای این کار استفاده کنید."
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 بازگشت", callback_data="donate_center")]]
    )
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()


__all__ = ["router"]
