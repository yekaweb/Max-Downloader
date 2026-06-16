"""Referral handler – Max Youtube Downloader"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.repositories import UserRepository
from database.connection import AsyncSessionLocal
from services import ReferralService, CoinTransactionService
from utils.helpers import generate_referral_code

router = Router()


@router.message(Command("referral"))
async def show_referral(message: Message, **kwargs):
    """نمایش برنامه معرفی و کد کاربر"""
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)

        if not user:
            await message.reply("❌ کاربر یافت نشد. لطفاً /start را بزنید.")
            return

        # Generate referral code if not exists
        if not user.referral_code:
            referral_code = generate_referral_code()
            user = await user_repo.update(
                message.from_user.id,
                referral_code=referral_code
            )

        # Get referral stats
        ref_service = ReferralService(session)
        completed_count = await ref_service.get_user_referral_count(user.id)

        bot_username = "Max_youtube_downloader_bot"
        referral_link = f"https://t.me/{bot_username}?start={user.referral_code}"

        referral_text = (
            "🎁 <b>برنامه معرفی به دوستان</b>\n\n"
            f"📌 <b>کد شما:</b> <code>{user.referral_code}</code>\n"
            f"🔗 <b>لینک دعوت:</b>\n{referral_link}\n\n"
            f"👥 <b>دوستان دعوت شده:</b> {completed_count} نفر\n"
            f"💰 <b>کل سکه‌های دریافتی:</b> {int(user.total_coins or 0)} سکه\n"
            f"💎 <b>موجودی فعلی:</b> {int(user.total_coins or 0)} سکه\n\n"
            "<b>نحوه کار:</b>\n"
            "۱. لینک یا کد خود را برای دوستان بفرستید.\n"
            "۲. آنها با لینک شما وارد ربات شوند.\n"
            "۳. شما <b>۵۰ سکه</b> هدیه می‌گیرید!\n"
            "۴. دوست شما <b>۱۰۰ سکه</b> هدیه ورود می‌گیرد!\n\n"
            "<b>کاربرد سکه‌ها:</b>\n"
            "تبدیل به اشتراک ویژه (هر ۱۰۰ سکه = ۱ ماه رایگان)"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📤 ارسال لینک برای دوستان", url=f"https://t.me/share/url?url={referral_link}&text=سلام!%20من%20از%20ربات%20Max%20Downloader%20استفاده%20میکنم.%20با%20این%20لینک%20وارد%20شو%20و%20100%20سکه%20هدیه%20بگیر!")],
                [InlineKeyboardButton(text="📊 تاریخچه معرفی", callback_data="referral_history")],
                [InlineKeyboardButton(text="💳 تبدیل سکه به اشتراک", callback_data="coins_convert")],
            ]
        )

        await message.reply(referral_text, reply_markup=keyboard, parse_mode="HTML")


@router.message(Command("coins"))
async def show_coins(message: Message, **kwargs):
    """نمایش موجودی سکه و تاریخچه تراکنش‌ها"""
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)

        if not user:
            await message.reply("❌ کاربر یافت نشد.")
            return

        coin_service = CoinTransactionService(session)
        stats = await coin_service.get_transaction_stats(user.id)
        transactions = await coin_service.get_user_transactions(user.id, limit=10)

        coin_text = (
            "💰 <b>کیف پول سکه شما</b>\n\n"
            f"💎 <b>موجودی فعلی:</b> {int(user.total_coins or 0)} سکه\n"
            f"📈 <b>کل دریافتی:</b> {int(stats['total_earned'])} سکه\n"
            f"📉 <b>کل مصرف شده:</b> {int(stats['total_spent'])} سکه\n\n"
            "<b>آخرین تراکنش‌ها:</b>"
        )

        if transactions:
            for tx in transactions[:10]:
                emoji = "➕" if tx.amount > 0 else "➖"
                amount = abs(tx.amount)
                # Translate transaction type
                tx_type = tx.transaction_type
                if tx_type == "referral_reward":
                    tx_type = "هدیه معرفی"
                elif tx_type == "welcome_bonus":
                    tx_type = "هدیه ورود"
                elif tx_type == "subscription_purchase":
                    tx_type = "خرید اشتراک"
                
                coin_text += f"\n{emoji} {tx_type}: {int(amount)} سکه"
        else:
            coin_text += "\nهنوز تراکنشی نداشته‌اید."

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🎁 دریافت سکه رایگان (معرفی)", callback_data="menu_referral")],
                [InlineKeyboardButton(text="💳 تبدیل به اشتراک", callback_data="coins_convert")],
            ]
        )

        await message.reply(coin_text, reply_markup=keyboard, parse_mode="HTML")


__all__ = ["router", "show_referral", "show_coins"]
