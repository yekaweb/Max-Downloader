"""Subscription service"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Subscription, Plan, User
from sqlalchemy import select
from utils.db_utils import scalars_first, scalars_all, scalar_value


class SubscriptionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_subscription(self, user_id: int) -> Subscription:
        result = await self.db.execute(
            select(Subscription).where(
                (Subscription.user_id == user_id) &
                (Subscription.is_active == True)
            )
        )
        return await scalars_first(result)

    async def get_user_plan(self, user_id: int) -> Plan:
        result = await self.db.execute(
            select(Plan).join(Subscription).where(
                (Subscription.user_id == user_id) &
                (Subscription.is_active == True)
            )
        )
        return await scalars_first(result)

    async def check_user_limits(self, user_id: int) -> Dict[str, Any]:
        subscription = await self.get_user_subscription(user_id)
        plan = await self.get_user_plan(user_id)
        
        if not plan:
            return {"has_limits": True, "daily_limit": 5, "max_file_size": 50 * 1024 * 1024, "quality_limit": "720p"}
        
        return {
            "has_limits": plan.download_limit is not None,
            "daily_limit": plan.download_limit,
            "max_file_size": plan.max_file_size,
            "quality_limit": plan.quality_limit,
        }

    async def can_user_download(self, user_id: int) -> tuple[bool, str]:
        """Check if user is allowed to download based on their plan limits."""
        from database.models import Download
        from datetime import datetime, time
        from sqlalchemy import func
        
        limits = await self.check_user_limits(user_id)
        
        if not limits["has_limits"]:
            return True, ""
            
        daily_limit = limits.get("daily_limit")
        if daily_limit is None:
            return True, ""
            
        # Count today's downloads
        today_start = datetime.combine(datetime.today(), time.min)
        
        result = await self.db.execute(
            select(func.count(Download.id)).where(
                (Download.user_id == user_id) &
                (Download.created_at >= today_start) &
                (Download.status != "failed")
            )
        )
        today_count = await scalar_value(result) or 0
        
        if today_count >= daily_limit:
            return False, f"شما به سقف دانلود روزانه ({daily_limit} فایل) رسیده‌اید. برای دانلود بیشتر حساب خود را ارتقا دهید."
            
        return True, ""

    async def activate_subscription(self, user_id: int, plan_id: int, duration_days: int = 30) -> Subscription:
        """Activate or extend a subscription for a user."""
        from datetime import datetime, timedelta
        
        # Deactivate existing active subscriptions
        result = await self.db.execute(
            select(Subscription).where(
                (Subscription.user_id == user_id) &
                (Subscription.is_active == True)
            )
        )
        existing_subs = await scalars_all(result)
        for sub in existing_subs:
            sub.is_active = False
            
        # Create new subscription
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration_days)
        
        new_sub = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            auto_renew=True
        )
        self.db.add(new_sub)
        await self.db.commit()
        await self.db.refresh(new_sub)
        return new_sub

    async def upgrade_plan_with_coins(self, user_id: int, plan_id: int, coin_cost: float, duration_days: int = 30) -> tuple[bool, str]:
        """Exchange coins for a subscription plan."""
        from database.models import User, CoinTransaction
        
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = await scalars_first(result)
        
        if not user or user.total_coins < coin_cost:
            return False, "سکه کافی برای خرید این پلن ندارید."
            
        # Deduct coins
        user.total_coins -= coin_cost
        
        # Log transaction
        tx = CoinTransaction(
            user_id=user.id,
            amount=-coin_cost,
            transaction_type="plan_upgrade",
            description=f"Exchanged {coin_cost} coins for plan ID {plan_id}"
        )
        self.db.add(tx)
        
        # Activate subscription
        await self.activate_subscription(user_id, plan_id, duration_days)
        
        return True, "اشتراک شما با موفقیت از طریق سکه فعال شد!"

__all__ = ["SubscriptionService"]
