"""Comprehensive Cache Service for Download Management"""
import hashlib
import aiofiles
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.cached_download_repo import CachedDownloadRepository
from database.models.cached_download import CachedDownload
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """
    Service for managing download cache
    
    Features:
    - Calculate file hash (SHA256)
    - Check if URL is cached
    - Save downloaded files to cache
    - Retrieve cached file_ids from database
    - Invalidate expired cache
    - Cleanup old cache entries
    """
    
    @staticmethod
    async def calculate_file_hash(file_path: str) -> str:
        """
        Calculate SHA256 hash of file for deduplication
        
        Args:
            file_path: Path to file
        
        Returns:
            SHA256 hash string (hexdigest)
        
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If read fails
        """
        sha256_hash = hashlib.sha256()
        
        try:
            # Read file in chunks (memory efficient)
            async with aiofiles.open(file_path, "rb") as f:
                while True:
                    chunk = await f.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    sha256_hash.update(chunk)
            
            hash_hex = sha256_hash.hexdigest()
            logger.debug(f"Calculated hash for {file_path}: {hash_hex}")
            return hash_hex
        
        except FileNotFoundError:
            logger.error(f"File not found for hash calculation: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error calculating hash: {e}")
            raise
    
    @staticmethod
    async def get_cached_file_id(
        url: str,
        session: AsyncSession,
        quality: Optional[str] = None
    ) -> Optional[str]:
        """
        Get cached Telegram file_id for URL
        
        If found, automatically marks cache as used (increment download_count)
        
        Args:
            url: Original download URL
            session: Database session
            quality: Optional quality filter (1080p, 720p, audio, etc)
        
        Returns:
            Telegram file_id if cached and valid, None otherwise
        
        Example:
            >>> file_id = await CacheService.get_cached_file_id(
            ...     "https://youtube.com/watch?v=xyz",
            ...     session
            ... )
            >>> if file_id:
            ...     await message.reply_document(file_id)
        """
        try:
            repo = CachedDownloadRepository(session)
            cached_list = await repo.find_valid_by_url(url)
            
            if not cached_list:
                logger.info(f"No cache found for URL: {url}")
                return None
            
            # Select best match based on quality if specified
            selected_cache = None
            if quality:
                for cache in cached_list:
                    if quality.lower() in cache.quality.lower():
                        selected_cache = cache
                        break
            
            # If no quality match or not specified, take first (newest)
            if not selected_cache:
                selected_cache = cached_list[0]
            
            # Mark cache as used
            await repo.mark_used(selected_cache.id)
            
            logger.info(
                f"Cache HIT - URL: {url} | Quality: {selected_cache.quality} | "
                f"File ID: {selected_cache.telegram_file_id[:20]}... | "
                f"Downloads: {selected_cache.download_count + 1}"
            )
            
            return selected_cache.telegram_file_id
        
        except Exception as e:
            logger.error(f"Error retrieving cache: {e}")
            return None
    
    @staticmethod
    async def get_all_cached_versions(
        url: str,
        session: AsyncSession
    ) -> list[CachedDownload]:
        """
        Get all valid cached versions for a URL (different qualities)
        
        Useful for showing user multiple options instead of re-downloading
        
        Args:
            url: Original download URL
            session: Database session
        
        Returns:
            List of CachedDownload objects (ordered by newest first)
        
        Example:
            >>> versions = await CacheService.get_all_cached_versions(url, session)
            >>> for v in versions:
            ...     print(f"{v.quality} - {v.file_size_mb:.1f}MB")
        """
        try:
            repo = CachedDownloadRepository(session)
            versions = await repo.find_valid_by_url(url)
            logger.debug(f"Found {len(versions)} cached version(s) for URL: {url}")
            return versions
        except Exception as e:
            logger.error(f"Error getting cached versions: {e}")
            return []
    
    @staticmethod
    async def save_to_cache(
        url: str,
        telegram_file_id: str,
        file_info: Dict[str, Any],
        session: AsyncSession,
        expire_days: int = 30
    ) -> Optional[CachedDownload]:
        """
        Save downloaded file to cache
        
        Args:
            url: Original URL
            telegram_file_id: Telegram's file ID for this file
            file_info: Dictionary with keys:
                - title: str (video title)
                - platform: str (youtube, instagram, etc)
                - duration: int (seconds, optional)
                - uploader: str (video uploader, optional)
                - size: int (bytes, IMPORTANT)
                - file_type: str (video/mp4, audio/mpeg, etc)
                - quality: str (1080p, 720p, 320kbps, etc)
                - codec: str (h264, vp9, mp3, aac, etc)
                - container: str (mp4, mkv, webm, m4a, etc)
                - width: int (optional)
                - height: int (optional)
                - thumb_url: str (optional)
            session: Database session
            expire_days: Cache expiration in days (default 30)
        
        Returns:
            CachedDownload object if saved, None if error
        
        Example:
            >>> info = {
            ...     'title': 'Video Title',
            ...     'platform': 'youtube',
            ...     'size': 52428800,  # 50MB
            ...     'quality': '1080p',
            ...     'codec': 'h264',
            ...     'container': 'mp4',
            ...     'file_type': 'video/mp4'
            ... }
            >>> cache = await CacheService.save_to_cache(url, file_id, info, session)
        """
        try:
            # Validate required fields
            required_fields = ['title', 'platform', 'size', 'file_type', 
                             'quality', 'codec', 'container']
            missing = [f for f in required_fields if f not in file_info]
            if missing:
                logger.warning(f"Missing fields in file_info: {missing}")
            
            repo = CachedDownloadRepository(session)
            
            # Calculate expire date
            expires_at = datetime.utcnow() + timedelta(days=expire_days)
            
            # Create cache entry
            cached = await repo.create_from_upload(
                source_url=url,
                source_platform=file_info.get('platform', 'unknown'),
                media_title=file_info.get('title', 'Unknown')[:500],
                media_duration=file_info.get('duration'),
                media_uploader=file_info.get('uploader'),
                telegram_file_id=telegram_file_id,
                file_size=file_info.get('size', 0),
                file_type=file_info.get('file_type', 'application/octet-stream'),
                quality=file_info.get('quality', 'unknown'),
                format_codec=file_info.get('codec', 'unknown'),
                format_container=file_info.get('container', 'unknown'),
                resolution_width=file_info.get('width'),
                resolution_height=file_info.get('height'),
                expires_at=expires_at
            )
            
            logger.info(
                f"Saved to cache - URL: {url} | Title: {cached.media_title[:50]} | "
                f"Size: {cached.file_size_mb:.1f}MB | Quality: {cached.quality} | "
                f"Expires: {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            )
            
            return cached
        
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
            return None
    
    @staticmethod
    async def invalidate_cache(
        cache_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Mark cache entry as invalid/expired
        
        Called when telegram_file_id is no longer valid (expired)
        
        Args:
            cache_id: Cache entry ID
            session: Database session
        
        Returns:
            True if invalidated, False if error
        
        Example:
            >>> success = await CacheService.invalidate_cache(123, session)
        """
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
        """
        Delete expired cache entries
        
        Args:
            session: Database session
            older_than_days: Delete entries older than this (default 30)
        
        Returns:
            Number of deleted entries
        """
        try:
            from sqlalchemy import delete
            from sqlalchemy.ext.asyncio import AsyncSession
            
            repo = CachedDownloadRepository(session)
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            
            # Count before deletion
            result = await session.execute(
                delete(CachedDownload).where(
                    (CachedDownload.expires_at != None) &
                    (CachedDownload.expires_at < cutoff_date)
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
        Get cache statistics
        
        Returns:
            Dictionary with:
            - total_entries: Total cached items
            - valid_entries: Non-expired items
            - total_size_mb: Total size in MB
            - most_downloaded: (quality, count) tuple
            - oldest_cache: creation date of oldest cache
            - newest_cache: creation date of newest cache
        """
        try:
            from sqlalchemy import func, select
            
            # Count entries
            total_result = await session.execute(select(func.count(CachedDownload.id)))
            total_entries = total_result.scalar() or 0
            
            # Count valid entries
            valid_result = await session.execute(
                select(func.count(CachedDownload.id)).where(
                    (CachedDownload.expires_at == None) |
                    (CachedDownload.expires_at > datetime.utcnow())
                )
            )
            valid_entries = valid_result.scalar() or 0
            
            # Total size
            size_result = await session.execute(
                select(func.sum(CachedDownload.file_size))
            )
            total_bytes = size_result.scalar() or 0
            total_size_mb = total_bytes / (1024 * 1024)
            
            # Most downloaded quality
            most_downloaded = await session.execute(
                select(CachedDownload.quality, func.count(CachedDownload.id))
                .group_by(CachedDownload.quality)
                .order_by(func.count(CachedDownload.id).desc())
                .limit(1)
            )
            most_dl = most_downloaded.first() or (None, 0)
            
            stats = {
                'total_entries': total_entries,
                'valid_entries': valid_entries,
                'total_size_mb': round(total_size_mb, 2),
                'most_downloaded_quality': most_dl[0],
                'most_downloaded_count': most_dl[1]
            }
            
            logger.info(f"Cache stats: {stats}")
            return stats
        
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}


__all__ = ["CacheService"]
