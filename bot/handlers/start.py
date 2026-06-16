"""Start handler: /start and language selection with referral integration"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from config import settings
from services import ReferralService
from database.repositories import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database.models.models import User
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession = None):
    """
    /start command handler with referral code processing.
    """
    try:
        user = message.from_user
        user_id = user.id
        
        # Parse referral code
        args = message.text.split()
        referral_code = args[1] if len(args) > 1 else None
        
        # Get user stats if session is available
        user_downloads = 0
        total_users = 0
        
        if session:
            try:
                user_repo = UserRepository(session)
                db_user = await user_repo.get_by_telegram_id(user_id)
                if db_user:
                    user_downloads = db_user.total_downloads or 0
                
                # Get total users count for quick stats
                result = await session.execute(select(func.count(User.id)))
                total_users = result.scalar() or 0
            except Exception as e:
                logger.error(f"Error fetching stats: {e}")
        
        kb = [
            [KeyboardButton(text="📥 دانلود جدید (ارسال لینک)"), KeyboardButton(text="👤 پروفایل من")],
            [KeyboardButton(text="💳 خرید اشتراک / سکه"), KeyboardButton(text="👥 معرفی به دوستان")],
            [KeyboardButton(text="📊 تاریخچه دانلودها"), KeyboardButton(text="🆘 راهنما / پشتیبانی")],
            [KeyboardButton(text="⚙️ تنظیمات")]
        ]
        
        # Add Admin button if user is admin
        if user_id in settings.ADMIN_IDS_LIST:
            kb.append([KeyboardButton(text="🛠 پنل مدیریت (Admin)")])
            
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="لینک خود را بفرستید...")
        
        # Professional welcome message
        welcome_msg = (
            f"👋 سلام <b>{user.first_name}</b> عزیز! به ربات <b>Max Youtube Downloader</b> خوش آمدید.\n\n"
            f"🚀 <b>قدرتمندترین و سریع‌ترین ربات دانلودر تلگرام</b>\n"
            f"شما می‌توانید لینک ویدیو یا آهنگ مورد نظر خود را از ده‌ها پلتفرم (یوتیوب، اینستاگرام، تیک‌تاک و...) ارسال کنید و آن را با بالاترین کیفیت ممکن دریافت کنید!\n\n"
        )
        
        # Add quick stats
        if user_downloads > 0 or total_users > 0:
            welcome_msg += "📊 <b>آمار سریع:</b>\n"
            if user_downloads > 0:
                welcome_msg += f"📥 دانلودهای شما: {user_downloads} فایل\n"
            if total_users > 0:
                welcome_msg += f"👥 کاربران فعال: {total_users} نفر\n"
            welcome_msg += "\n"
            
        welcome_msg += "برای شروع، فقط کافیست لینک خود را همینجا بفرستید 👇"
        
        # Process referral code if provided
        if referral_code and session:
            try:
                ref_service = ReferralService(session)
                is_valid, msg, referrer = await ref_service.is_referral_valid(referral_code, current_user_id=user_id)
                
                if is_valid and referrer:
                    referral = await ref_service.create_referral(referrer_id=referrer.id, referred_user_id=user_id)
                    success, coin_msg = await ref_service.mark_referral_complete(referral.id)
                    
                    if success:
                        welcome_msg += f"\n\n🎁 <b>هدیه دعوت:</b>\n✅ {coin_msg}\n💰 شما ۵۰ سکه رایگان دریافت کردید!"
                    else:
                        welcome_msg += f"\n\n⚠️ {coin_msg}"
                else:
                    welcome_msg += f"\n\n⚠️ کد معرفی معتبر نیست: {msg}"
            except Exception as e:
                logger.error(f"Error processing referral code: {e}")
        
        await message.reply(welcome_msg, parse_mode="HTML", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await message.reply("❌ خطایی رخ داد. لطفاً دوباره سعی کنید.")

__all__ = ["router"]
