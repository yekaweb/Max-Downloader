"""
Cache Handler - Manage cached downloads and file_id storage
"""

import asyncio
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from loguru import logger
from database.models.cached_download import CachedDownload


class CacheManager:
    """Manage cached downloads in database"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def find_cached_downloads(self, source_url: str) -> List[CachedDownload]:
        """
        Find all cached versions of a URL
        
        Returns list of CachedDownload objects sorted by size (best first)
        """
        try:
            stmt = (
                select(CachedDownload)
                .where(CachedDownload.source_url == source_url)
                .order_by(desc(CachedDownload.file_size))
            )
            result = await self.db.execute(stmt)
            cached = result.scalars().all()
            logger.info(f"✅ Found {len(cached)} cached versions for: {source_url[:50]}")
            return cached
        except Exception as e:
            logger.error(f"Error finding cached downloads: {e}")
            return []
    
    async def save_cached_download(
        self,
        source_url: str,
        source_platform: str,
        media_title: str,
        telegram_file_id: str,
        file_size: int,
        file_type: str,
        quality: str,
        format_codec: str,
        format_container: str,
        resolution_width: Optional[int] = None,
        resolution_height: Optional[int] = None,
        media_duration: Optional[int] = None,
        media_uploader: Optional[str] = None,
    ) -> Optional[CachedDownload]:
        """
        Save a successful download to cache
        """
        try:
            cached = CachedDownload(
                source_url=source_url,
                source_platform=source_platform,
                media_title=media_title,
                telegram_file_id=telegram_file_id,
                file_size=file_size,
                file_type=file_type,
                quality=quality,
                format_codec=format_codec,
                format_container=format_container,
                resolution_width=resolution_width,
                resolution_height=resolution_height,
                media_duration=media_duration,
                media_uploader=media_uploader,
            )
            self.db.add(cached)
            await self.db.commit()
            await self.db.refresh(cached)
            logger.info(
                f"✅ Cached: {media_title[:50]} | {quality} | "
                f"{file_size / 1024 / 1024:.1f}MB | file_id:{telegram_file_id[:20]}"
            )
            return cached
        except Exception as e:
            logger.error(f"Error saving cached download: {e}")
            await self.db.rollback()
            return None
    
    async def increment_usage_count(self, cached_id: int) -> bool:
        """Increment download count for cached file"""
        try:
            stmt = select(CachedDownload).where(CachedDownload.id == cached_id)
            result = await self.db.execute(stmt)
            cached = result.scalars().first()
            if cached:
                cached.download_count += 1
                cached.last_used_at = datetime.now()
                await self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating cache usage: {e}")
            await self.db.rollback()
            return False
    
    async def delete_cached_download(self, cached_id: int) -> bool:
        """Delete cached download record"""
        try:
            stmt = select(CachedDownload).where(CachedDownload.id == cached_id)
            result = await self.db.execute(stmt)
            cached = result.scalars().first()
            if cached:
                await self.db.delete(cached)
                await self.db.commit()
                logger.info(f"✅ Deleted cache: {cached.media_title[:50]}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting cached download: {e}")
            await self.db.rollback()
            return False
    
    async def get_cache_statistics(self) -> dict:
        """Get cache statistics"""
        try:
            total_cached_stmt = select(func.count()).select_from(CachedDownload)
            total_size_stmt = select(func.sum(CachedDownload.file_size))
            total_uses_stmt = select(func.sum(CachedDownload.download_count))

            total_cached = (await self.db.execute(total_cached_stmt)).scalar() or 0
            total_size = (await self.db.execute(total_size_stmt)).scalar() or 0
            total_uses = (await self.db.execute(total_uses_stmt)).scalar() or 0

            return {
                "total_cached_files": total_cached,
                "total_cache_size_gb": total_size / (1024**3),
                "total_cache_uses": total_uses,
            }
        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {}


def format_cached_list_message(cached_downloads: List[CachedDownload]) -> str:
    """
    Format cached downloads for user display
    
    Output example:
    ✅ 2 فایل داخل دیتابیس پیدا شد
    
    برای ادامه و دریافت فرمت های بیشتر روی دکمه 🆕 کلیک کنید.
    
    شماره: 1
    اسم: معماری تونل ریورس...
    اندازه: 10.68 MB
    دانلود شده در: 2026-05-26 10:47:28
    زمان: 348s
    نوع: video/x-matroska
    وضوح: 1280x720
    
    ────────────────
    
    شماره: 2
    ...
    """
    
    if not cached_downloads:
        return "❌ فایل کش‌شده‌ای برای این لینک پیدا نشد"
    
    message = f"✅ {len(cached_downloads)} فایل داخل دیتابیس پیدا شد\n\n"
    message += "برای ادامه و دریافت فرمت های بیشتر روی دکمه 🆕 کلیک کنید.\n\n"
    
    for idx, cached in enumerate(cached_downloads, 1):
        message += f"شماره: {idx}\n"
        message += f"اسم: {cached.media_title[:50]}\n"
        message += f"اندازه: {cached.file_size_mb:.2f} MB\n"
        message += f"دانلود شده در: {cached.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if cached.media_duration:
            minutes, seconds = divmod(cached.media_duration, 60)
            hours, minutes = divmod(minutes, 60)
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            message += f"زمان: {duration_str}\n"
        
        message += f"نوع: {cached.file_type}\n"
        message += f"کیفیت: {cached.quality} | کدک: {cached.format_codec}\n"
        
        if cached.resolution_str != "N/A":
            message += f"وضوح: {cached.resolution_str}\n"
        
        message += f"تعداد دفعات استفاده: {cached.download_count}\n"
        message += "────────────────\n\n"
    
    return message


__all__ = ["CacheManager", "format_cached_list_message"]
