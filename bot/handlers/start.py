"""Start handler: /start and language selection with referral integration"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from config import settings
from services import ReferralService
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession = None):
    """
    /start command handler with referral code processing.
    
    Usage:
    - /start - Normal start
    - /start ABC12345 - Start with referral code
    """
    try:
        lang = settings.DEFAULT_LANGUAGE
        user = message.from_user
        user_id = user.id
        
        # Extract referral code from message if provided
        # Format: /start <referral_code>
        args = message.text.split()
        referral_code = args[1] if len(args) > 1 else None
        
        welcome_msg = f"سلام {user.first_name}! به DLBot خوش آمدید. (زبان: {lang})"
        
        # Process referral code if provided
        if referral_code and session:
            try:
                ref_service = ReferralService(session)
                
                # Validate referral code
                is_valid, msg, referrer = await ref_service.is_referral_valid(
                    referral_code,
                    current_user_id=user_id
                )
                
                if is_valid and referrer:
                    # Create referral
                    referral = await ref_service.create_referral(
                        referrer_id=referrer.id,
                        referred_user_id=user_id
                    )
                    
                    # Mark as complete - automatically awards coins
                    success, coin_msg = await ref_service.mark_referral_complete(referral.id)
                    
                    if success:
                        welcome_msg += f"\n\n✅ {coin_msg}"
                        welcome_msg += f"\n💰 شما و معرف شما به ترتیب 100 و 50 سکه دریافت کردید!"
                    else:
                        logger.warning(f"Failed to mark referral complete: {coin_msg}")
                        welcome_msg += f"\n⚠️ {coin_msg}"
                else:
                    welcome_msg += f"\n⚠️ کد معرفی معتبر نیست: {msg}"
                    
            except Exception as e:
                logger.error(f"Error processing referral code: {e}")
                welcome_msg += "\n⚠️ خطا در پردازش کد معرفی"
        
        await message.reply(welcome_msg)
        
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await message.reply("❌ خطایی رخ داد. لطفاً دوباره سعی کنید.")

__all__ = ["router"]
