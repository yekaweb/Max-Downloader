"""Download Repository"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Download


class DownloadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, **kwargs) -> Download:
        download = Download(user_id=user_id, **kwargs)
        self.db.add(download)
        await self.db.commit()
        await self.db.refresh(download)
        return download

    async def get_by_id(self, download_id: int) -> Download:
        result = await self.db.execute(
            select(Download).where(Download.id == download_id)
        )
        return result.scalars().first()

    async def get_user_downloads(self, user_id: int, limit: int = 100):
        result = await self.db.execute(
            select(Download).where(Download.user_id == user_id).limit(limit)
        )
        return result.scalars().all()


__all__ = ["DownloadRepository"]
