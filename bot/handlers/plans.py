"""Plans handler - subscription plans"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


@router.message(Command("plans"))
async def show_plans(message: Message):
    """Show available plans"""
    plans_text = """
💳 **Available Plans**

🆓 **FREE**
- Download limit: 5/day
- Max quality: 720p
- Price: FREE

⭐ **PREMIUM**
- Download limit: Unlimited
- Max quality: 1080p
- Price: $5/month

🚀 **VIP**
- Download limit: Unlimited
- Max quality: 4K
- Support: Priority
- Price: $15/month
"""
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Premium - $5", callback_data="plan_premium")],
            [InlineKeyboardButton(text="VIP - $15", callback_data="plan_vip")],
        ]
    )
    
    await message.reply(plans_text, reply_markup=keyboard, parse_mode="Markdown")


__all__ = ["router"]
