"""
PHASE 1: Cache Cleanup Tasks
Celery tasks for automatic cache management (cleanup old, limit size, etc)
"""

from celery import shared_task
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select, delete, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from database.models.cached_download import CachedDownload, CachedQuality
from database.repositories.cached_download_repo import CachedDownloadRepository
from config_simple import settings
from services.comprehensive_cache_service import CacheService
import logging

logger = logging.getLogger(__name__)


@shared_task(name='cleanup_expired_cache')
def cleanup_expired_cache(older_than_days: int = 30):
    """
    Celery task: Remove expired cache entries
    
    Run: Every day at 2 AM (configure in Celery beat)
    
    Args:
        older_than_days: Delete entries expired more than X days ago
    
    Returns:
        Dictionary with {status, deleted_count, cleaned_size_mb}
    """
    try:
        logger.info(f"[CLEANUP] Starting cleanup of expired cache (older than {older_than_days} days)")
        
        import asyncio
        
        async def cleanup():
            # Create session
            engine = create_async_engine(settings.DATABASE_URL, echo=False)
            async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            
            async with async_session() as session:
                # Calculate cutoff date
                cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
                
                # Count before deletion
                count_result = await session.execute(
                    select(func.count(CachedDownload.id)).where(
                        (CachedDownload.expires_at != None) &
                        (CachedDownload.expires_at < cutoff_date)
                    )
                )
                count_before = count_result.scalar() or 0
                
                # Delete expired entries
                await session.execute(
                    delete(CachedDownload).where(
                        (CachedDownload.expires_at != None) &
                        (CachedDownload.expires_at < cutoff_date)
                    )
                )
                await session.commit()
                
                logger.info(f"[CLEANUP] Deleted {count_before} expired cache entries")
                return {'deleted': count_before}
        
        # Run async function
        result = asyncio.run(cleanup())
        
        return {
            'status': 'success',
            'deleted_count': result.get('deleted', 0),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"[CLEANUP] Error during cleanup: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(name='limit_cache_size')
def limit_cache_size(max_size_gb: int = 5):
    """
    Celery task: Limit total cache size using LRU strategy
    
    If total cache size exceeds max_size_gb, delete least recently used entries
    
    Run: Every 6 hours (configure in Celery beat)
    
    Args:
        max_size_gb: Maximum total cache size in GB
    
    Returns:
        Dictionary with {status, freed_mb, deleted_count}
    """
    try:
        logger.info(f"[SIZE LIMIT] Checking cache size limit ({max_size_gb}GB)")
        
        import asyncio
        
        async def limit_size():
            # Create session
            engine = create_async_engine(settings.DATABASE_URL, echo=False)
            async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            
            async with async_session() as session:
                # Get total size
                size_result = await session.execute(
                    select(func.sum(CachedQuality.file_size))
                )
                total_bytes = size_result.scalar() or 0
                total_mb = total_bytes / (1024 * 1024)
                max_bytes = max_size_gb * 1024 * 1024 * 1024
                
                logger.info(f"[SIZE LIMIT] Current size: {total_mb:.1f}MB / {max_size_gb * 1024:.0f}MB")
                
                if total_bytes <= max_bytes:
                    logger.info("[SIZE LIMIT] Cache size within limit")
                    return {'status': 'ok', 'current_mb': total_mb}
                
                # Need to free up space
                bytes_to_free = total_bytes - max_bytes
                mb_to_free = bytes_to_free / (1024 * 1024)
                logger.warning(f"[SIZE LIMIT] Exceeding limit by {mb_to_free:.1f}MB, using LRU")
                
                # Get LRU entries (oldest used entries)
                lru_result = await session.execute(
                    select(CachedDownload)
                    .order_by(CachedDownload.last_accessed.asc())
                    .limit(1000)  # Safety limit
                )
                
                lru_entries = lru_result.scalars().all()
                freed = 0
                deleted = 0
                
                for entry in lru_entries:
                    if freed >= bytes_to_free:
                        break
                    # Sum file sizes from qualities
                    for q in entry.qualities:
                        freed += q.file_size or 0
                    await session.delete(entry)
                    deleted += 1
                
                await session.commit()
                
                freed_mb = freed / (1024 * 1024)
                logger.info(f"[SIZE LIMIT] Freed {freed_mb:.1f}MB by deleting {deleted} entries")
                
                return {'freed_mb': freed_mb, 'deleted': deleted}
        
        # Run async function
        result = asyncio.run(limit_size())
        
        return {
            'status': 'success',
            **result,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"[SIZE LIMIT] Error: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(name='cache_statistics')
def cache_statistics():
    """
    Celery task: Generate cache statistics
    
    Run: Daily for monitoring
    
    Returns:
        Dictionary with cache stats
    """
    try:
        logger.info("[STATS] Generating cache statistics")
        
        import asyncio
        
        async def get_stats():
            # Create session
            engine = create_async_engine(settings.DATABASE_URL, echo=False)
            async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            
            async with async_session() as session:
                # Total entries
                total_result = await session.execute(select(func.count(CachedDownload.id)))
                total = total_result.scalar() or 0
                
                # Valid entries
                valid_result = await session.execute(
                    select(func.count(CachedDownload.id)).where(
                        (CachedDownload.expires_at == None) |
                        (CachedDownload.expires_at > datetime.utcnow())
                    )
                )
                valid = valid_result.scalar() or 0
                
                # Total size
                size_result = await session.execute(
                    select(func.sum(CachedQuality.file_size))
                )
                total_bytes = size_result.scalar() or 0
                
                # Average file size
                avg_size = total_bytes / total if total > 0 else 0
                
                # Most popular platform
                platform_result = await session.execute(
                    select(CachedDownload.platform, func.count(CachedDownload.id))
                    .group_by(CachedDownload.platform)
                    .order_by(func.count(CachedDownload.id).desc())
                    .limit(1)
                )
                top_platform = platform_result.first() or ('unknown', 0)
                
                # Most popular quality
                quality_result = await session.execute(
                    select(CachedQuality.quality_label, func.count(CachedDownload.id))
                    .group_by(CachedQuality.quality_label)
                    .order_by(func.count(CachedDownload.id).desc())
                    .limit(1)
                )
                top_quality = quality_result.first() or ('unknown', 0)
                
                stats = {
                    'total_entries': total,
                    'valid_entries': valid,
                    'expired_entries': total - valid,
                    'total_size_mb': round(total_bytes / (1024 * 1024), 2),
                    'total_size_gb': round(total_bytes / (1024 * 1024 * 1024), 2),
                    'average_file_size_mb': round(avg_size / (1024 * 1024), 2),
                    'top_platform': top_platform[0],
                    'top_platform_count': top_platform[1],
                    'top_quality': top_quality[0],
                    'top_quality_count': top_quality[1]
                }
                
                logger.info(f"[STATS] {stats}")
                return stats
        
        # Run async function
        stats = asyncio.run(get_stats())
        
        return {
            'status': 'success',
            'statistics': stats,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"[STATS] Error: {e}")
        return {'status': 'failed', 'error': str(e)}


# ============================================
# CELERY BEAT SCHEDULE
# ============================================
# Add to celery_app.py or settings:
#
# from celery.schedules import crontab
#
# app.conf.beat_schedule = {
#     # ... existing tasks ...
#     
#     # PHASE 1: Cache Management
#     'cleanup-expired-cache': {
#         'task': 'tasks.cleanup_tasks.cleanup_expired_cache',
#         'schedule': crontab(hour=2, minute=0),  # 2 AM daily
#         'args': (30,)  # Delete entries expired 30+ days ago
#     },
#     'limit-cache-size': {
#         'task': 'tasks.cleanup_tasks.limit_cache_size',
#         'schedule': crontab(hour='*/6'),  # Every 6 hours
#         'args': (5,)  # Keep max 5GB
#     },
#     'cache-statistics': {
#         'task': 'tasks.cleanup_tasks.cache_statistics',
#         'schedule': crontab(hour=1, minute=0),  # 1 AM daily
#     }
# }


__all__ = [
    'cleanup_expired_cache',
    'limit_cache_size',
    'cache_statistics'
]
