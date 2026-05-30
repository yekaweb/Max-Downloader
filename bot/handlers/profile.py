"""Profile handler - user profile and statistics"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.repositories import UserRepository
from database.connection import AsyncSessionLocal

router = Router()


@router.message(Command("profile"))
async def show_profile(message: Message):
    """Show user profile"""
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(message.from_user.id)
        
        if not user:
            await message.reply("❌ User not found")
            return
        
        profile_text = f"""
👤 **Your Profile**

📝 **Name**: {user.first_name} {user.last_name or ''}
🆔 **ID**: `{user.telegram_id}`
🌐 **Language**: {user.language}
📊 **Downloads**: {user.total_downloads}
💰 **Coins**: {user.total_coins}
📅 **Joined**: {user.created_at.strftime('%Y-%m-%d')}

🎁 **Referral Code**: `{user.referral_code or 'Not generated'}`
📈 **Referrals**: {user.referral_count}
"""
        await message.reply(profile_text, parse_mode="Markdown")


__all__ = ["router"]
