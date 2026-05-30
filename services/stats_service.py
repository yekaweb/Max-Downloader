"""Statistics service"""
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Download, Payment
from sqlalchemy import select, func


class StatsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_total_users(self) -> int:
        result = await self.db.execute(select(func.count(User.id)))
        return result.scalar() or 0

    async def get_total_downloads(self) -> int:
        result = await self.db.execute(select(func.count(Download.id)))
        return result.scalar() or 0

    async def get_total_revenue(self) -> float:
        result = await self.db.execute(
            select(func.sum(Payment.amount)).where(Payment.status == "completed")
        )
        return result.scalar() or 0

    async def get_active_users_today(self) -> int:
        from datetime import datetime, timedelta
        today = datetime.now().date()
        result = await self.db.execute(
            select(func.count(User.id)).where(
                func.date(User.last_active_at) == today
            )
        )
        return result.scalar() or 0


__all__ = ["StatsService"]
