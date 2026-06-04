"""Repository for CachedDownload model"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_
from database.models.cached_download import CachedDownload
from datetime import datetime


class CachedDownloadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_url(self, source_url: str):
        stmt = select(CachedDownload).where(CachedDownload.source_url == source_url)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_valid_by_url(self, source_url: str):
        # Return cached entries that are not expired (expires_at is null or in the future)
        now = datetime.utcnow()
        stmt = (
            select(CachedDownload)
            .where(
                CachedDownload.source_url == source_url,
                or_(CachedDownload.expires_at == None, CachedDownload.expires_at > now),
            )
            .order_by(CachedDownload.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_from_upload(
        self,
        source_url: str,
        source_platform: str,
        media_title: str,
        media_duration: int,
        media_uploader: str,
        telegram_file_id: str,
        file_size: int,
        file_type: str,
        quality: str,
        format_codec: str,
        format_container: str,
        resolution_width: int | None = None,
        resolution_height: int | None = None,
        expires_at: datetime | None = None,
    ) -> CachedDownload:
        cd = CachedDownload(
            source_url=source_url,
            source_platform=source_platform,
            media_title=media_title,
            media_duration=media_duration,
            media_uploader=media_uploader,
            telegram_file_id=telegram_file_id,
            file_size=file_size,
            file_type=file_type,
            quality=quality,
            format_codec=format_codec,
            format_container=format_container,
            resolution_width=resolution_width,
            resolution_height=resolution_height,
            expires_at=expires_at,
        )
        self.db.add(cd)
        await self.db.commit()
        await self.db.refresh(cd)
        return cd

    async def mark_used(self, cached_id: int):
        stmt = update(CachedDownload).where(CachedDownload.id == cached_id).values(
            download_count=CachedDownload.download_count + 1,
            last_used_at=datetime.utcnow(),
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def mark_invalid(self, cached_id: int):
        """Mark a cached download as invalid/expired so it won't be returned."""
        stmt = update(CachedDownload).where(CachedDownload.id == cached_id).values(
            expires_at=datetime.utcnow()
        )
        await self.db.execute(stmt)
        await self.db.commit()


__all__ = ["CachedDownloadRepository"]
