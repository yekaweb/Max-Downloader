"""Comprehensive Cache Service for Pro Cache System"""
import hashlib
import aiofiles
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from database.repositories.cached_download_repo import CachedDownloadRepository
from database.models.cached_download import CachedDownload, CachedQuality
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """
    Service for managing Pro Cache (two-table architecture).

    Features:
    - Calculate file hash (SHA256)
    - Check if URL is cached (by URL hash)
    - Save downloaded files to cache (CachedDownload + CachedQuality)
    - Retrieve cached file_ids from database
    - Invalidate expired cache
    - Cleanup old cache entries
    """

    @staticmethod
    async def calculate_file_hash(file_path: str) -> str:
        """Calculate SHA256 hash of file for deduplication"""
        sha256_hash = hashlib.sha256()
        try:
            async with aiofiles.open(file_path, "rb") as f:
                while True:
                    chunk = await f.read(8192)
                    if not chunk:
                        break
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            logger.error(f"File not found for hash: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error calculating hash: {e}")
            raise

    @staticmethod
    async def get_cached_file_id(
        url_hash: str,
        session: AsyncSession,
        quality: Optional[str] = None
    ) -> Optional[str]:
        """
        Get cached Telegram file_id for a URL hash.

        Args:
            url_hash: SHA-256 hash of normalized URL
            session: Database session
            quality: Optional quality filter (e.g. '1080p', '720p')

        Returns:
            Telegram file_id if cached and valid, None otherwise
        """
        try:
            repo = CachedDownloadRepository(session)
            cached_download = await repo.find_valid_by_url_hash(url_hash)

            if not cached_download or not cached_download.qualities:
                logger.info(f"No cache found for hash: {url_hash[:12]}...")
                return None

            # Select best quality match
            selected_quality = None
            if quality:
                for q in cached_download.qualities:
                    if quality.lower() in q.quality_label.lower():
                        selected_quality = q
                        break

            if not selected_quality:
                selected_quality = cached_download.qualities[0]

            # Mark as used
            await repo.mark_used(cached_download.id, selected_quality.id)

            logger.info(
                f"Cache HIT - hash: {url_hash[:12]}... | "
                f"Quality: {selected_quality.quality_label} | "
                f"Downloads: {selected_quality.download_count + 1}"
            )

            return selected_quality.telegram_file_id

        except Exception as e:
            logger.error(f"Error retrieving cache: {e}")
            return None

    @staticmethod
    async def get_all_cached_versions(
        url_hash: str,
        session: AsyncSession
    ) -> List[CachedQuality]:
        """
        Get all valid cached qualities for a URL hash.

        Returns:
            List of CachedQuality objects
        """
        try:
            repo = CachedDownloadRepository(session)
            cached_download = await repo.find_valid_by_url_hash(url_hash)

            if not cached_download:
                return []

            qualities = cached_download.qualities or []
            logger.debug(f"Found {len(qualities)} cached qualities for hash: {url_hash[:12]}...")
            return list(qualities)
        except Exception as e:
            logger.error(f"Error getting cached versions: {e}")
            return []

    @staticmethod
    async def save_to_cache(
        url: str,
        url_hash: str,
        telegram_file_id: str,
        file_info: Dict[str, Any],
        session: AsyncSession,
        expire_days: int = 30
    ) -> Optional[CachedQuality]:
        """
        Save downloaded file to Pro Cache.

        Args:
            url: Original URL
            url_hash: SHA-256 hash of normalized URL
            telegram_file_id: Telegram's file ID
            file_info: Dictionary with keys:
                - title, platform, duration, uploader
                - size, file_type, quality, codec, container
                - width, height, thumb_url
            session: Database session
            expire_days: Cache expiration in days

        Returns:
            CachedQuality object if saved, None if error
        """
        try:
            repo = CachedDownloadRepository(session)
            expires_at = datetime.utcnow() + timedelta(days=expire_days)

            # Check if CachedDownload already exists
            cached_download = await repo.find_by_url_hash(url_hash)

            if not cached_download:
                # Create new CachedDownload
                cached_download = await repo.create_download(
                    url_hash=url_hash,
                    original_url=url,
                    platform=file_info.get('platform', 'unknown'),
                    title=file_info.get('title', 'Unknown')[:500],
                    duration=file_info.get('duration'),
                    uploader=file_info.get('uploader'),
                    thumbnail_url=file_info.get('thumb_url'),
                    expires_at=expires_at,
                )

            # Create CachedQuality
            quality = await repo.create_quality(
                cache_id=cached_download.id,
                quality_label=file_info.get('quality', 'unknown'),
                telegram_file_id=telegram_file_id,
                file_size=file_info.get('size', 0),
                mime_type=file_info.get('file_type', 'application/octet-stream'),
                extension=file_info.get('container', 'unknown'),
                resolution=(
                    f"{file_info.get('width')}x{file_info.get('height')}"
                    if file_info.get('width') and file_info.get('height') else None
                ),
                video_codec=file_info.get('codec') if 'video' in file_info.get('file_type', '') else None,
                audio_codec=file_info.get('codec') if 'audio' in file_info.get('file_type', '') else None,
            )

            logger.info(
                f"Saved to cache - hash: {url_hash[:12]}... | "
                f"Quality: {quality.quality_label} | "
                f"Size: {quality.file_size_mb:.1f}MB | "
                f"Expires: {expires_at.strftime('%Y-%m-%d %H:%M')}"
            )

            return quality

        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
            return None

    @staticmethod
    async def invalidate_cache(
        cache_id: int,
        session: AsyncSession
    ) -> bool:
        """Mark cache entry as invalid/expired"""
        try:
            repo = CachedDownloadRepository(session)
            await repo.mark_invalid(cache_id)
            logger.info(f"Invalidated cache entry: {cache_id}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False

    @staticmethod
    async def cleanup_expired(
        session: AsyncSession,
        older_than_days: int = 30
    ) -> int:
        """Delete expired cache entries"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)

            # Delete expired qualities first (cascading)
            result = await session.execute(
                delete(CachedDownload).where(
                    CachedDownload.expires_at != None,
                    CachedDownload.expires_at < cutoff_date
                )
            )

            deleted_count = result.rowcount
            await session.commit()

            logger.info(f"Cleanup: Deleted {deleted_count} expired cache entries")
            return deleted_count

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0

    @staticmethod
    async def get_cache_stats(
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with total_entries, valid_entries, total_size_mb, etc.
        """
        try:
            # Count total CachedDownload entries
            total_result = await session.execute(
                select(func.count(CachedDownload.id))
            )
            total_entries = total_result.scalar() or 0

            # Count valid entries
            valid_result = await session.execute(
                select(func.count(CachedDownload.id)).where(
                    (CachedDownload.expires_at == None) |
                    (CachedDownload.expires_at > datetime.utcnow())
                )
            )
            valid_entries = valid_result.scalar() or 0

            # Total size from CachedQuality
            size_result = await session.execute(
                select(func.sum(CachedQuality.file_size))
            )
            total_bytes = size_result.scalar() or 0
            total_size_mb = total_bytes / (1024 * 1024)

            # Most downloaded quality
            most_dl_result = await session.execute(
                select(
                    CachedQuality.quality_label,
                    func.count(CachedQuality.id)
                )
                .group_by(CachedQuality.quality_label)
                .order_by(func.count(CachedQuality.id).desc())
                .limit(1)
            )
            most_dl = most_dl_result.first() or (None, 0)

            # Count total qualities
            qual_result = await session.execute(
                select(func.count(CachedQuality.id))
            )
            total_qualities = qual_result.scalar() or 0

            stats = {
                'total_entries': total_entries,
                'valid_entries': valid_entries,
                'total_qualities': total_qualities,
                'total_size_mb': round(total_size_mb, 2),
                'most_downloaded_quality': most_dl[0],
                'most_downloaded_count': most_dl[1],
            }

            logger.info(f"Cache stats: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}


__all__ = ["CacheService"]
