"""
Repository for CachedDownload + CachedQuality models
Pro Cache - hash-based lookup with multi-quality support
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_, and_
from sqlalchemy.orm import selectinload
from database.models.cached_download import CachedDownload, CachedQuality
from datetime import datetime
from typing import Optional, List


class CachedDownloadRepository:
    """Repository for CachedDownload (one row per URL)"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── URL Hash-based Lookup ──────────────────────────────────────────

    async def find_by_url_hash(self, url_hash: str) -> Optional[CachedDownload]:
        """Find cached download by URL hash (with qualities eager-loaded)"""
        stmt = (
            select(CachedDownload)
            .options(selectinload(CachedDownload.qualities))
            .where(CachedDownload.url_hash == url_hash)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_valid_by_url_hash(self, url_hash: str) -> Optional[CachedDownload]:
        """Find valid (non-expired) cached download by URL hash"""
        now = datetime.utcnow()
        stmt = (
            select(CachedDownload)
            .options(selectinload(CachedDownload.qualities))
            .where(
                CachedDownload.url_hash == url_hash,
                CachedDownload.is_valid == True,
                or_(
                    CachedDownload.expires_at == None,
                    CachedDownload.expires_at > now
                )
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ── Legacy URL-based lookup (for backward compat) ──────────────────

    async def find_by_url(self, original_url: str) -> List[CachedDownload]:
        """Find ALL cached downloads matching original_url (legacy)"""
        stmt = (
            select(CachedDownload)
            .options(selectinload(CachedDownload.qualities))
            .where(CachedDownload.original_url == original_url)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_valid_by_url(self, original_url: str) -> List[CachedDownload]:
        """Find valid cached downloads by original URL (legacy)"""
        now = datetime.utcnow()
        stmt = (
            select(CachedDownload)
            .options(selectinload(CachedDownload.qualities))
            .where(
                CachedDownload.original_url == original_url,
                CachedDownload.is_valid == True,
                or_(
                    CachedDownload.expires_at == None,
                    CachedDownload.expires_at > now
                )
            )
            .order_by(CachedDownload.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # ── Create ─────────────────────────────────────────────────────────

    async def create_download(
        self,
        url_hash: str,
        original_url: str,
        platform: str,
        title: Optional[str] = None,
        duration: Optional[int] = None,
        uploader: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        normalized_url: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> CachedDownload:
        """Create a new cached download entry"""
        cd = CachedDownload(
            url_hash=url_hash,
            original_url=original_url,
            normalized_url=normalized_url or original_url,
            platform=platform,
            title=title,
            duration=duration,
            uploader=uploader,
            thumbnail_url=thumbnail_url,
            expires_at=expires_at,
        )
        self.db.add(cd)
        await self.db.commit()
        await self.db.refresh(cd)
        return cd

    async def create_quality(
        self,
        cache_id: int,
        quality_label: str,
        telegram_file_id: str,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
        extension: Optional[str] = None,
        resolution: Optional[str] = None,
        video_codec: Optional[str] = None,
        audio_codec: Optional[str] = None,
        bitrate: Optional[int] = None,
        fps: Optional[int] = None,
        format_id: Optional[str] = None,
    ) -> CachedQuality:
        """Add a quality entry to an existing cached download"""
        cq = CachedQuality(
            cache_id=cache_id,
            quality_label=quality_label,
            telegram_file_id=telegram_file_id,
            file_size=file_size,
            mime_type=mime_type,
            extension=extension,
            resolution=resolution,
            video_codec=video_codec,
            audio_codec=audio_codec,
            bitrate=bitrate,
            fps=fps,
            format_id=format_id,
        )
        self.db.add(cq)
        await self.db.commit()
        await self.db.refresh(cq)
        return cq

    # ── Create from upload (backward compat) ───────────────────────────

    async def create_from_upload(
        self,
        source_url: str,
        source_platform: str,
        media_title: str,
        media_duration: Optional[int],
        media_uploader: Optional[str],
        telegram_file_id: str,
        file_size: int,
        file_type: str,
        quality: str,
        format_codec: str,
        format_container: str,
        resolution_width: Optional[int] = None,
        resolution_height: Optional[int] = None,
        expires_at: Optional[datetime] = None,
        url_hash: Optional[str] = None,
    ) -> CachedDownload:
        """
        Legacy-compatible create method.
        Creates a CachedDownload with one CachedQuality.
        """
        if url_hash is None:
            import hashlib
            url_hash = hashlib.sha256(source_url.encode()).hexdigest()

        # Check if download already exists
        existing = await self.find_by_url_hash(url_hash)
        if existing:
            # Add new quality to existing download
            await self.create_quality(
                cache_id=existing.id,
                quality_label=quality,
                telegram_file_id=telegram_file_id,
                file_size=file_size,
                mime_type=file_type,
                extension=format_container,
                resolution=(
                    f"{resolution_width}x{resolution_height}"
                    if resolution_width and resolution_height else None
                ),
                video_codec=format_codec if 'video' in (file_type or '') else None,
                audio_codec=format_codec if 'audio' in (file_type or '') else None,
            )
            return existing

        # Create new download
        cd = await self.create_download(
            url_hash=url_hash,
            original_url=source_url,
            platform=source_platform,
            title=media_title[:500] if media_title else None,
            duration=media_duration,
            uploader=media_uploader,
            expires_at=expires_at,
        )

        # Add quality
        await self.create_quality(
            cache_id=cd.id,
            quality_label=quality,
            telegram_file_id=telegram_file_id,
            file_size=file_size,
            mime_type=file_type,
            extension=format_container,
            resolution=(
                f"{resolution_width}x{resolution_height}"
                if resolution_width and resolution_height else None
            ),
            video_codec=format_codec if 'video' in (file_type or '') else None,
            audio_codec=format_codec if 'audio' in (file_type or '') else None,
        )

        return cd

    # ── Quality operations ─────────────────────────────────────────────

    async def get_qualities(self, cache_id: int) -> List[CachedQuality]:
        """Get all qualities for a cached download"""
        stmt = (
            select(CachedQuality)
            .where(CachedQuality.cache_id == cache_id)
            .order_by(CachedQuality.quality_label)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_quality_by_id(self, quality_id: int) -> Optional[CachedQuality]:
        """Get a specific quality by ID"""
        return await self.db.get(CachedQuality, quality_id)

    async def get_quality_by_file_id(self, file_id: str) -> Optional[CachedQuality]:
        """Get quality by Telegram file_id"""
        stmt = select(CachedQuality).where(CachedQuality.telegram_file_id == file_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ── Mark / Update ──────────────────────────────────────────────────

    async def mark_used(self, cached_id: int, quality_id: Optional[int] = None):
        """Mark cache entry as used (increment counters)"""
        now = datetime.utcnow()

        # Update download-level stats
        stmt = (
            update(CachedDownload)
            .where(CachedDownload.id == cached_id)
            .values(
                access_count=CachedDownload.access_count + 1,
                last_accessed=now,
            )
        )
        await self.db.execute(stmt)

        # Update quality-level stats if specified
        if quality_id:
            stmt = (
                update(CachedQuality)
                .where(CachedQuality.id == quality_id)
                .values(
                    download_count=CachedQuality.download_count + 1,
                    last_downloaded=now,
                )
            )
            await self.db.execute(stmt)

        await self.db.commit()

    async def mark_invalid(self, cached_id: int):
        """Mark a cached download as invalid/expired"""
        stmt = (
            update(CachedDownload)
            .where(CachedDownload.id == cached_id)
            .values(is_valid=False, expires_at=datetime.utcnow())
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def delete_quality(self, quality_id: int):
        """Delete a specific quality entry"""
        stmt = delete(CachedQuality).where(CachedQuality.id == quality_id)
        await self.db.execute(stmt)
        await self.db.commit()


__all__ = ["CachedDownloadRepository"]
