"""Referral handler - manage user referral program and coin rewards"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.repositories import UserRepository
from database.connection import AsyncSessionLocal
from services import ReferralService, CoinTransactionService
from utils.helpers import generate_referral_code

router = Router()


@router.message(Command("referral"))
async def show_referral(message: Message):
    """Show referral information and manage referral code"""
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        
        if not user:
            await message.reply("❌ User not found")
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
        
        referral_text = f"""
🎁 **Your Referral Program**

📌 **Your Code**: `{user.referral_code}`
👥 **Completed Referrals**: {completed_count}
💰 **Total Coins Earned**: {user.total_coins:.0f} coins
💎 **Current Balance**: {user.total_coins:.0f} coins

**How it works:**
• Share your code with friends
• They join using your code
• You get 50 coins per successful referral
• They get 100 coins as sign-up bonus

**Coin uses:**
💳 Convert to subscription (100 coins = 1 month Free)
🎁 Stack for bigger rewards
"""
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📤 Share Code", callback_data="referral_share")],
                [InlineKeyboardButton(text="📊 View History", callback_data="referral_history")],
                [InlineKeyboardButton(text="💳 Convert to Subscription", callback_data="coins_convert")],
            ]
        )
        
        await message.reply(referral_text, reply_markup=keyboard, parse_mode="Markdown")


@router.message(Command("coins"))
async def show_coins(message: Message):
    """Show coin balance and transaction history"""
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        
        if not user:
            await message.reply("❌ User not found")
            return
        
        coin_service = CoinTransactionService(session)
        stats = await coin_service.get_transaction_stats(user.id)
        transactions = await coin_service.get_user_transactions(user.id, limit=10)
        
        coin_text = f"""
💰 **Your Coin Wallet**

💎 **Current Balance**: {user.total_coins:.0f} coins
📈 **Total Earned**: {stats['total_earned']:.0f} coins
📉 **Total Spent**: {stats['total_spent']:.0f} coins

**Recent Transactions:**
"""
        
        if transactions:
            for tx in transactions[:10]:
                emoji = "➕" if tx.amount > 0 else "➖"
                amount = abs(tx.amount)
                coin_text += f"\n{emoji} {tx.transaction_type.capitalize()}: {amount:.0f} coins"
        else:
            coin_text += "\nNo transactions yet"
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🎁 Referral", url="/referral")],
                [InlineKeyboardButton(text="💳 Convert to Subscription", callback_data="coins_convert")],
            ]
        )
        
        await message.reply(coin_text, reply_markup=keyboard, parse_mode="Markdown")


__all__ = ["router"]
