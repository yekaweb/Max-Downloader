"""
Integration guide for coin earning on downloads
This file shows WHERE and HOW to integrate coin earning into the download flow

File: bot/handlers/download.py (EXAMPLE - modify your actual download handler)
"""

# Example integration points for coin earning:

# ============================================================================
# INTEGRATION POINT 1: Download Completion
# ============================================================================
# Location: In your download completion handler, after successful upload
# Add this after file is successfully sent to user:

async def on_download_complete(user_id: int, downloaded_size_bytes: int):
    """
    Award coins for successful download completion.
    
    Earning Formula:
    - 10 coins per 100MB downloaded
    - Minimum 5 coins per download
    - Maximum 1000 coins per file
    
    Examples:
    - 50 MB file → 5 coins (minimum)
    - 100 MB file → 10 coins
    - 250 MB file → 25 coins
    - 1000 MB (1 GB) file → 100 coins
    - 1500 MB file → 150 coins (but capped at 1000 max)
    """
    from services import CoinTransactionService
    from database.connection import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        coin_service = CoinTransactionService(session)
        
        # Calculate coins earned
        downloaded_mb = downloaded_size_bytes / (1024 * 1024)
        coins_earned = int(downloaded_mb / 100 * 10)  # 10 coins per 100MB
        coins_earned = max(5, min(coins_earned, 1000))  # Clamp 5-1000
        
        # Award coins
        transaction = await coin_service.add_coins(
            user_id=user_id,
            amount=coins_earned,
            transaction_type="download",
            description=f"Download completed ({downloaded_mb:.1f} MB)"
        )
        
        return coins_earned, transaction


# ============================================================================
# INTEGRATION POINT 2: Referral Signup Completion
# ============================================================================
# Location: In your user registration handler (/start command), 
# after user is created, check for referral code

async def process_referral_signup(user_id: int, referral_code: str = None):
    """
    Process referral signup and award coins to both parties.
    
    This should be called right after user registration.
    """
    from services import ReferralService
    from database.connection import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        ref_service = ReferralService(session)
        
        if not referral_code:
            return  # No referral code
        
        # Validate referral code
        is_valid, message, referrer = await ref_service.is_referral_valid(
            referral_code, 
            current_user_id=user_id
        )
        
        if not is_valid:
            # Log invalid referral attempt but don't fail signup
            logger.warning(f"Invalid referral code: {referral_code}")
            return
        
        # Create referral relationship
        referral = await ref_service.create_referral(
            referrer_id=referrer.id,
            referred_user_id=user_id
        )
        
        # Mark as completed and award coins
        success, msg = await ref_service.mark_referral_complete(
            referral.id,
            referrer_reward=50.0,  # 50 coins for referrer
            referred_reward=100.0   # 100 coins for new user
        )
        
        if success:
            logger.info(f"Referral completed: {referrer.id} → {user_id}")


# ============================================================================
# INTEGRATION POINT 3: Admin Award Bonus Coins
# ============================================================================
# Create/add this to bot/handlers/admin/bonus.py or admin.py

async def award_bonus_coins(
    user_telegram_id: int,
    coins: float,
    reason: str = "Admin reward"
):
    """
    Award bonus coins to user (admin action).
    Should be behind admin verification.
    """
    from services import CoinTransactionService
    from database.repositories import UserRepository
    from database.connection import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # Verify user exists
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(user_telegram_id)
        
        if not user:
            return False, "User not found"
        
        # Award coins
        coin_service = CoinTransactionService(session)
        transaction = await coin_service.bonus_coins(
            user_id=user.id,
            amount=coins,
            reason=reason
        )
        
        return True, f"Awarded {coins:.0f} coins to user {user.telegram_id}"


# ============================================================================
# EXAMPLE: Complete Download Flow with Coin Earning
# ============================================================================

async def complete_download_example(message: Message, download_url: str):
    """
    Example of a complete download handler with coin earning integrated.
    
    This shows the full flow:
    1. Download the file
    2. Upload to Telegram
    3. Award coins
    4. Update UI with earned coins
    """
    from services import CoinTransactionService
    from database.repositories import UserRepository
    from database.connection import AsyncSessionLocal
    
    try:
        # 1. Get user
        async with AsyncSessionLocal() as session:
            user_repo = UserRepository(session)
            user = await user_repo.get_by_telegram_id(message.from_user.id)
        
        # 2. Download file (implementation details omitted)
        progress_message = await message.reply("⬇️ Downloading...")
        file_path = await download_file(download_url, progress_message)
        file_size = os.path.getsize(file_path)
        
        # 3. Upload to Telegram (implementation details omitted)
        progress_message = await message.edit_text("⬆️ Uploading to Telegram...")
        await upload_to_telegram(message.bot, file_path, message.chat.id)
        
        # 4. Award coins
        async with AsyncSessionLocal() as session:
            coin_service = CoinTransactionService(session)
            
            # Calculate and award coins
            downloaded_mb = file_size / (1024 * 1024)
            coins_earned = int(downloaded_mb / 100 * 10)
            coins_earned = max(5, min(coins_earned, 1000))
            
            await coin_service.add_coins(
                user_id=user.id,
                amount=coins_earned,
                transaction_type="download",
                description=f"Download completed ({downloaded_mb:.1f} MB)"
            )
        
        # 5. Show completion message with coin info
        await message.edit_text(
            f"✅ Download complete!\n"
            f"File size: {downloaded_mb:.1f} MB\n"
            f"💎 Coins earned: +{coins_earned}\n"
            f"💰 Total coins: {user.total_coins + coins_earned:.0f}"
        )
        
    except Exception as e:
        logger.error(f"Download failed: {e}")
        await message.reply(f"❌ Download failed: {str(e)}")


# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# These should be moved to config.py or environment variables

COIN_CONFIG = {
    "download_coins_per_100mb": 10,
    "download_coins_min": 5,
    "download_coins_max": 1000,
    
    "referral_coins_signup": 100,
    "referral_coins_referrer": 50,
    "referral_coins_download": 10,  # Future: bonus coins for referral's first download
    
    "coins_per_month_subscription": 100,
    
    "bonus_coins_max_admin_per_user": 10000,
}


# ============================================================================
# TESTING COIN EARNING
# ============================================================================

import asyncio

async def test_coin_earning():
    """Test script to verify coin earning works"""
    from database.connection import AsyncSessionLocal
    from database.repositories import UserRepository
    from services import CoinTransactionService
    
    async with AsyncSessionLocal() as session:
        # Create test user (or use existing)
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(123456)  # Test user ID
        
        if not user:
            user = await user_repo.create(
                telegram_id=123456,
                first_name="TestUser"
            )
        
        # Test coin earning
        coin_service = CoinTransactionService(session)
        
        # Test 1: Award coins
        tx1 = await coin_service.add_coins(
            user_id=user.id,
            amount=100,
            transaction_type="test",
            description="Test earning"
        )
        print(f"✅ Earned 100 coins: {tx1}")
        
        # Test 2: Get balance
        balance = await coin_service.get_user_balance(user.id)
        print(f"✅ Current balance: {balance}")
        
        # Test 3: Spend coins
        success, msg, tx = await coin_service.spend_coins(
            user_id=user.id,
            amount=50,
            description="Test spending"
        )
        print(f"✅ Spent coins: {msg}")
        
        # Test 4: Get stats
        stats = await coin_service.get_transaction_stats(user.id)
        print(f"✅ Stats: {stats}")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_coin_earning())
