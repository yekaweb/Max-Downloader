"""Subscription service"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Subscription, Plan, User
from sqlalchemy import select


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
        return result.scalars().first()

    async def get_user_plan(self, user_id: int) -> Plan:
        result = await self.db.execute(
            select(Plan).join(Subscription).where(
                (Subscription.user_id == user_id) &
                (Subscription.is_active == True)
            )
        )
        return result.scalars().first()

    async def check_user_limits(self, user_id: int) -> Dict[str, Any]:
        subscription = await self.get_user_subscription(user_id)
        plan = await self.get_user_plan(user_id)
        
        if not plan:
            return {"has_limits": True, "daily_limit": 5}
        
        return {
            "has_limits": plan.download_limit is not None,
            "daily_limit": plan.download_limit,
            "max_file_size": plan.max_file_size,
            "quality_limit": plan.quality_limit,
        }


__all__ = ["SubscriptionService"]
