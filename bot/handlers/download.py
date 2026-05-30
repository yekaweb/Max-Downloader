"""Download handler with coin earning integration"""
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from bot.states.download import DownloadStates
from bot.keyboards.inline import get_quality_keyboard
from services import CoinTransactionService
from database.models import User
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message()
async def handle_url(message: types.Message, state: FSMContext, session: AsyncSession):
    """Handle URL submission for download"""
    if not message.text or not message.text.startswith("http"):
        await message.reply("❌ لطفاً یک لینک معتبر ارسال کنید")
        return
    
    # Store URL in state
    await state.set_state(DownloadStates.selecting_format)
    await state.update_data(url=message.text)
    
    # Ask for quality selection
    await message.reply(
        "📊 لطفاً کیفیت مورد نظر را انتخاب کنید:",
        reply_markup=get_quality_keyboard()
    )


async def award_download_coins(
    user_id: int,
    file_size_bytes: float,
    session: AsyncSession
) -> tuple[bool, str, int]:
    """
    Award coins for download completion.
    
    Formula: 10 coins per 100MB
    Min: 5 coins, Max: 1000 coins
    
    Args:
        user_id: User ID
        file_size_bytes: File size in bytes
        session: Database session
        
    Returns:
        (success, message, coins_awarded)
    """
    try:
        file_size_mb = file_size_bytes / (1024 * 1024)
        
        # Calculate coins: 10 per 100MB
        coins = int((file_size_mb / 100) * 10)
        # Apply min/max limits
        coins = max(5, min(coins, 1000))
        
        coin_service = CoinTransactionService(session)
        
        await coin_service.add_coins(
            user_id=user_id,
            amount=coins,
            transaction_type="download",
            description=f"Downloaded {file_size_mb:.1f} MB"
        )
        
        return True, f"🎉 +{coins} coins earned!", coins
    except Exception as e:
        logger.error(f"Error awarding download coins for user {user_id}: {e}")
        return False, "⚠️ Failed to award coins", 0


__all__ = ["router", "award_download_coins"]
