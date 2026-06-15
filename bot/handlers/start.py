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
        
        # Create a beautiful ReplyKeyboardMarkup
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        
        kb = [
            [KeyboardButton(text="📥 دانلود جدید (ارسال لینک)"), KeyboardButton(text="👤 پروفایل من")],
            [KeyboardButton(text="💳 خرید اشتراک / سکه"), KeyboardButton(text="👥 معرفی به دوستان")],
            [KeyboardButton(text="📊 تاریخچه دانلودها"), KeyboardButton(text="🆘 راهنما / پشتیبانی")],
            [KeyboardButton(text="⚙️ تنظیمات")]
        ]
        
        # Add Admin button if user is admin
        if user_id in settings.ADMIN_IDS:
            kb.append([KeyboardButton(text="🛠 پنل مدیریت (Admin)")])
            
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="لینک خود را بفرستید...")
        
        # Professional welcome message
        welcome_msg = (
            f"👋 سلام <b>{user.first_name}</b> عزیز! به ربات <b>Max Youtube Downloader</b> خوش آمدید.\n\n"
            f"🚀 <b>قدرتمندترین و سریع‌ترین ربات دانلودر تلگرام</b>\n"
            f"شما می‌توانید لینک ویدیو یا آهنگ مورد نظر خود را از ده‌ها پلتفرم (یوتیوب، اینستاگرام، تیک‌تاک و...) ارسال کنید و آن را با بالاترین کیفیت ممکن دریافت کنید!\n\n"
            f"برای شروع، فقط کافیست لینک خود را همینجا بفرستید 👇"
        )
        
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
                        welcome_msg += f"\n\n🎁 <b>هدیه دعوت:</b>"
                        welcome_msg += f"\n✅ {coin_msg}"
                        welcome_msg += f"\n💰 شما 50 سکه رایگان دریافت کردید!"
                    else:
                        logger.warning(f"Failed to mark referral complete: {coin_msg}")
                        welcome_msg += f"\n\n⚠️ {coin_msg}"
                else:
                    welcome_msg += f"\n\n⚠️ کد معرفی معتبر نیست: {msg}"
                    
            except Exception as e:
                logger.error(f"Error processing referral code: {e}")
                welcome_msg += "\n\n⚠️ خطا در پردازش کد معرفی"
        
        await message.reply(welcome_msg, parse_mode="HTML", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await message.reply("❌ خطایی رخ داد. لطفاً دوباره سعی کنید.")

__all__ = ["router"]
