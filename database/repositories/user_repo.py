"""User Repository"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_telegram_id(self, telegram_id: int) -> User:
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalars().first()

    async def create(self, telegram_id: int, **kwargs) -> User:
        user = User(telegram_id=telegram_id, **kwargs)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, telegram_id: int, **kwargs) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def delete(self, telegram_id: int) -> bool:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
            return True
        return False


__all__ = ["UserRepository"]
