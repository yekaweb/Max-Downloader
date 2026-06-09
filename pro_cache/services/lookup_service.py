"""
Cache Lookup Service for Pro Cache
سرویس جستجو و بازیابی از کش
"""

import logging
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
import json
import aioredis

from database.models import CachedDownload, CachedQuality
from database.connection import get_async_session


logger = logging.getLogger(__name__)


class CacheLookupService:
    """سرویس مدیریت جستجو در کش"""
    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self.redis = redis_client
        self.redis_ttl = timedelta(hours=24)  # TTL پیش‌فرض برای Redis
    
    async def find_cached_content(
        self, 
        url_hash: str
    ) -> Optional[CachedDownload]:
        """
        جستجوی محتوا در کش بر اساس hash
        
        Args:
            url_hash: هش URL
            
        Returns:
            شیء CachedDownload در صورت وجود، در غیر اینصورت None
        """
        try:
            # 1. ابتدا در Redis جستجو کنیم (اگر فعال باشد)
            if self.redis:
                redis_result = await self._check_redis_cache(url_hash)
                if redis_result:
                    logger.info(f"Cache hit in Redis for hash: {url_hash[:8]}...")
                    return redis_result
            
            # 2. اگر در Redis نبود، از دیتابیس بخوانیم
            async with get_async_session() as session:
                # Query با eager loading برای qualities
                query = (
                    select(CachedDownload)
                    .options(selectinload(CachedDownload.qualities))
                    .where(
                        CachedDownload.url_hash == url_hash,
                        CachedDownload.is_valid == True,
                        CachedDownload.expires_at > datetime.utcnow()
                    )
                )
                
                result = await session.execute(query)
                cached_content = result.scalar_one_or_none()
                
                if cached_content:
                    logger.info(f"Cache hit in DB for hash: {url_hash[:8]}...")
                    
                    # 3. بروزرسانی آمار دسترسی
                    await self._update_access_stats(session, cached_content.id)
                    
                    # 4. ذخیره در Redis برای دسترسی‌های بعدی
                    if self.redis:
                        await self._save_to_redis(cached_content)
                    
                    await session.commit()
                    return cached_content
                else:
                    logger.info(f"Cache miss for hash: {url_hash[:8]}...")
                    return None
                    
        except Exception as e:
            logger.error(f"Error in find_cached_content: {e}")
            return None
    
    async def get_cached_qualities(
        self, 
        url_hash: str
    ) -> List[CachedQuality]:
        """
        دریافت لیست کیفیت‌های کش شده برای یک URL
        
        Args:
            url_hash: هش URL
            
        Returns:
            لیست کیفیت‌های موجود
        """
        try:
            async with get_async_session() as session:
                # پیدا کردن cached_download
                cached_query = (
                    select(CachedDownload)
                    .where(
                        CachedDownload.url_hash == url_hash,
                        CachedDownload.is_valid == True
                    )
                )
                
                cached_result = await session.execute(cached_query)
                cached_download = cached_result.scalar_one_or_none()
                
                if not cached_download:
                    return []
                
                # دریافت کیفیت‌ها
                qualities_query = (
                    select(CachedQuality)
                    .where(CachedQuality.cache_id == cached_download.id)
                    .order_by(CachedQuality.quality_label)
                )
                
                qualities_result = await session.execute(qualities_query)
                qualities = qualities_result.scalars().all()
                
                return list(qualities)
                
        except Exception as e:
            logger.error(f"Error in get_cached_qualities: {e}")
            return []
    
    async def get_quality_by_id(
        self, 
        quality_id: int
    ) -> Optional[CachedQuality]:
        """
        دریافت اطلاعات یک کیفیت خاص
        
        Args:
            quality_id: شناسه کیفیت
            
        Returns:
            شیء CachedQuality یا None
        """
        try:
            async with get_async_session() as session:
                query = select(CachedQuality).where(CachedQuality.id == quality_id)
                result = await session.execute(query)
                return result.scalar_one_or_none()
                
        except Exception as e:
            logger.error(f"Error in get_quality_by_id: {e}")
            return None
    
    async def get_cached_by_id(
        self, 
        cache_id: int
    ) -> Optional[CachedDownload]:
        """
        دریافت اطلاعات کش بر اساس ID
        
        Args:
            cache_id: شناسه کش
            
        Returns:
            شیء CachedDownload یا None
        """
        try:
            async with get_async_session() as session:
                query = (
                    select(CachedDownload)
                    .options(selectinload(CachedDownload.qualities))
                    .where(CachedDownload.id == cache_id)
                )
                result = await session.execute(query)
                return result.scalar_one_or_none()
                
        except Exception as e:
            logger.error(f"Error in get_cached_by_id: {e}")
            return None
    
    async def update_access_stats(
        self, 
        quality_id: int
    ) -> bool:
        """
        بروزرسانی آمار دسترسی برای یک کیفیت
        
        Args:
            quality_id: شناسه کیفیت
            
        Returns:
            True در صورت موفقیت
        """
        try:
            async with get_async_session() as session:
                # بروزرسانی download_count و last_downloaded برای quality
                quality_update = (
                    update(CachedQuality)
                    .where(CachedQuality.id == quality_id)
                    .values(
                        download_count=CachedQuality.download_count + 1,
                        last_downloaded=datetime.utcnow()
                    )
                )
                await session.execute(quality_update)
                
                # دریافت cache_id برای بروزرسانی جدول اصلی
                quality_query = (
                    select(CachedQuality.cache_id)
                    .where(CachedQuality.id == quality_id)
                )
                quality_result = await session.execute(quality_query)
                cache_id = quality_result.scalar_one_or_none()
                
                if cache_id:
                    # بروزرسانی access_count و last_accessed برای cached_download
                    cache_update = (
                        update(CachedDownload)
                        .where(CachedDownload.id == cache_id)
                        .values(
                            access_count=CachedDownload.access_count + 1,
                            last_accessed=datetime.utcnow()
                        )
                    )
                    await session.execute(cache_update)
                
                await session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error in update_access_stats: {e}")
            return False
    
    async def check_cache_validity(
        self, 
        url_hash: str
    ) -> bool:
        """
        بررسی معتبر بودن کش
        
        Args:
            url_hash: هش URL
            
        Returns:
            True اگر کش معتبر باشد
        """
        try:
            async with get_async_session() as session:
                query = (
                    select(CachedDownload.is_valid, CachedDownload.expires_at)
                    .where(CachedDownload.url_hash == url_hash)
                )
                
                result = await session.execute(query)
                row = result.first()
                
                if not row:
                    return False
                
                is_valid, expires_at = row
                
                # بررسی validity و expiration
                return is_valid and expires_at > datetime.utcnow()
                
        except Exception as e:
            logger.error(f"Error in check_cache_validity: {e}")
            return False
    
    async def _check_redis_cache(
        self, 
        url_hash: str
    ) -> Optional[dict]:
        """
        بررسی کش در Redis
        
        Args:
            url_hash: هش URL
            
        Returns:
            دیکشنری داده‌ها یا None
        """
        try:
            redis_key = f"cache:content:{url_hash}"
            cached_data = await self.redis.get(redis_key)
            
            if cached_data:
                # Deserialize از JSON
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Redis cache check error: {e}")
            return None
    
    async def _save_to_redis(
        self, 
        cached_content: CachedDownload
    ) -> bool:
        """
        ذخیره داده‌ها در Redis
        
        Args:
            cached_content: محتوای کش شده
            
        Returns:
            True در صورت موفقیت
        """
        try:
            # تبدیل به دیکشنری قابل JSON
            cache_data = {
                'id': cached_content.id,
                'url_hash': cached_content.url_hash,
                'original_url': cached_content.original_url,
                'platform': cached_content.platform,
                'title': cached_content.title,
                'duration': cached_content.duration,
                'thumbnail_url': cached_content.thumbnail_url,
                'qualities': [
                    {
                        'id': q.id,
                        'quality_label': q.quality_label,
                        'file_size': q.file_size,
                        'telegram_file_id': q.telegram_file_id,
                        'extension': q.extension,
                        'mime_type': q.mime_type
                    } 
                    for q in cached_content.qualities
                ]
            }
            
            redis_key = f"cache:content:{cached_content.url_hash}"
            
            # ذخیره با TTL
            await self.redis.setex(
                redis_key,
                self.redis_ttl,
                json.dumps(cache_data, ensure_ascii=False)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Redis save error: {e}")
            return False
    
    async def _update_access_stats(
        self, 
        session, 
        cache_id: int
    ) -> None:
        """
        بروزرسانی آمار دسترسی در دیتابیس
        
        Args:
            session: نشست دیتابیس
            cache_id: شناسه کش
        """
        try:
            stmt = (
                update(CachedDownload)
                .where(CachedDownload.id == cache_id)
                .values(
                    access_count=CachedDownload.access_count + 1,
                    last_accessed=datetime.utcnow()
                )
            )
            await session.execute(stmt)
            
        except Exception as e:
            logger.error(f"Error updating access stats: {e}")