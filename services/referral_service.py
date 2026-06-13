"""Referral service - Manages referral system with milestone-based rewards"""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database.models import Referral, User, CoinTransaction
from loguru import logger
from utils.db_utils import scalars_first, scalars_all, scalar_value


class ReferralService:
    """Service for managing referral system and milestone-based rewards"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Base rewards configuration
    SIGN_UP_REWARD = 100.0  # Coins for signing up via referral
    REFERRER_REWARD = 50.0  # Base coins for referrer when someone joins
    
    # Milestone-based rewards (triggered at specific referral counts)
    MILESTONE_REWARDS = {
        1: {'coins': 10, 'badge': None, 'description': 'First referral'},
        5: {'coins': 50, 'badge': '⭐ دوستیابی ستاره', 'description': '5 Referrals milestone'},
        10: {'coins': 100, 'badge': '🌟 دوستیابی طلایی', 'description': '10 Referrals milestone'},
        20: {'coins': 200, 'badge': '👑 دوستیابی سلطنتی', 'description': '20 Referrals milestone'},
        50: {'coins': 500, 'badge': '💎 دوستیابی الماسی', 'description': '50 Referrals milestone'},
    }
    
    async def create_referral(self, referrer_id: int, referred_user_id: int) -> Referral:
        """Create a new referral link"""
        referral = Referral(
            referrer_id=referrer_id,
            referred_user_id=referred_user_id,
            status="pending"
        )
        self.db.add(referral)
        await self.db.commit()
        return referral
    
    async def mark_referral_complete(
        self,
        referral_id: int,
        referrer_reward: float = None,
        referred_reward: float = None
    ) -> tuple[bool, str]:
        """
        Complete a referral and award coins to both parties.
        
        Also checks for milestone rewards and awards them.
        
        Returns:
            (success, message)
        """
        referrer_reward = referrer_reward or self.REFERRER_REWARD
        referred_reward = referred_reward or self.SIGN_UP_REWARD
        
        result = await self.db.execute(
            select(Referral).where(Referral.id == referral_id)
        )
        referral = await scalars_first(result)
        
        if not referral:
            return False, "Referral not found"
        
        if referral.status == "completed":
            return False, "Referral already completed"
        
        try:
            # Mark referral as completed
            referral.status = "completed"
            referral.reward_coins = referrer_reward
            referral.completed_at = datetime.now()
            
            # Award coins to referrer
            referrer_tx = CoinTransaction(
                user_id=referral.referrer_id,
                amount=referrer_reward,
                transaction_type="referral",
                description=f"Referral reward: {referral.referred_user_id} joined"
            )
            self.db.add(referrer_tx)
            
            # Award coins to referred user
            referred_tx = CoinTransaction(
                user_id=referral.referred_user_id,
                amount=referred_reward,
                transaction_type="referral_signup",
                description="Sign-up bonus via referral"
            )
            self.db.add(referred_tx)
            
            # Update user coin balances
            result_ref = await self.db.execute(
                select(User).where(User.id == referral.referrer_id)
            )
            referrer = await scalars_first(result_ref)
            if referrer:
                referrer.total_coins += referrer_reward
                referrer.referral_count += 1
                self.db.add(referrer)
                
                # Check for milestone rewards
                await self._check_and_award_milestone(referrer)
            
            result_user = await self.db.execute(
                select(User).where(User.id == referral.referred_user_id)
            )
            referred_user = await scalars_first(result_user)
            if referred_user:
                referred_user.total_coins += referred_reward
                self.db.add(referred_user)
            
            await self.db.commit()
            return True, "Referral completed and coins awarded"
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error completing referral: {e}")
            return False, f"Error completing referral: {str(e)}"
    
    async def _check_and_award_milestone(self, user: User) -> None:
        """
        Check if user has reached a referral milestone and award bonus coins/badge.
        
        Called after each successful referral completion.
        Checks if current referral_count matches any milestone thresholds.
        """
        current_count = user.referral_count
        
        # Get previous milestone reached
        previous_milestone = getattr(user, 'referral_milestone', 0)
        
        # Check if current count reaches a new milestone
        for milestone_count in sorted(self.MILESTONE_REWARDS.keys()):
            if current_count >= milestone_count and milestone_count > previous_milestone:
                reward = self.MILESTONE_REWARDS[milestone_count]
                
                # Award milestone bonus coins
                bonus_coins = reward.get('coins', 0)
                milestone_tx = CoinTransaction(
                    user_id=user.id,
                    amount=bonus_coins,
                    transaction_type="referral_milestone",
                    description=f"Milestone reached: {reward['description']}"
                )
                self.db.add(milestone_tx)
                
                # Update user
                user.total_coins += bonus_coins
                user.referral_milestone = milestone_count
                
                # Award badge if applicable
                if reward.get('badge'):
                    user.referral_badge = reward['badge']
                
                logger.info(f"User {user.id} reached referral milestone {milestone_count}")
                logger.info(f"  Awarded: {bonus_coins} coins, Badge: {reward.get('badge')}")
    
    async def get_user_referrals(self, user_id: int, status: str = None):
        """Get referrals made by a user"""
        query = select(Referral).where(Referral.referrer_id == user_id)
        if status:
            query = query.where(Referral.status == status)
        
        result = await self.db.execute(query.order_by(Referral.created_at.desc()))
        return await scalars_all(result)
    
    async def get_user_referral_count(self, user_id: int) -> int:
        """Get count of completed referrals for a user"""
        result = await self.db.execute(
            select(func.count(Referral.id)).where(
                Referral.referrer_id == user_id,
                Referral.status == "completed"
            )
        )
        return await scalar_value(result) or 0
    
    async def get_referral_by_code(self, referral_code: str):
        """Get user by referral code"""
        result = await self.db.execute(
            select(User).where(User.referral_code == referral_code)
        )
        return await scalars_first(result)
    
    async def is_referral_valid(self, referral_code: str, current_user_id: int) -> tuple[bool, str, User]:
        """
        Validate referral code.
        
        Returns:
            (is_valid, message, referrer_user)
        """
        if not referral_code or len(referral_code) < 5:
            return False, "Invalid referral code", None
        
        referrer = await self.get_referral_by_code(referral_code)
        
        if not referrer:
            return False, "Referral code not found", None
        
        if referrer.id == current_user_id:
            return False, "Cannot use your own referral code", None
        
        return True, "Valid referral code", referrer


__all__ = ["ReferralService"]
