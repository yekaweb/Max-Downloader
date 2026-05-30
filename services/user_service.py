"""User service - user management and subscriptions"""
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories import UserRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get_user(self, telegram_id: int):
        return await self.repo.get_by_telegram_id(telegram_id)

    async def register_user(self, telegram_id: int, **kwargs):
        return await self.repo.create(telegram_id, **kwargs)

    async def update_user(self, telegram_id: int, **kwargs):
        return await self.repo.update(telegram_id, **kwargs)


__all__ = ["UserService"]
