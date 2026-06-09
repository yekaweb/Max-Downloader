# 📚 Pro Cache - راهنمای پیاده‌سازی گام به گام

## 🎯 هدف این راهنما

این سند برای توسعه‌دهندگانی که می‌خواهند Pro Cache را در پروژه Max-Downloader پیاده‌سازی کنند، تهیه شده است. تمام مراحل به صورت دقیق و با جزئیات کامل توضیح داده شده‌اند.

---

## 📋 پیش‌نیازها

### نرم‌افزارهای مورد نیاز
```bash
# Python 3.11+
python --version  # باید 3.11 یا بالاتر باشد

# PostgreSQL 15+
psql --version

# Redis 7+
redis-server --version

# Git
git --version
```

### کتابخانه‌های Python
```bash
pip install aiogram==3.4.1
pip install sqlalchemy==2.0.25
pip install alembic==1.13.1
pip install aioredis==2.0.1
pip install asyncpg==0.29.0
pip install python-dotenv==1.0.0
```

---

## 🚀 مرحله 1: راه‌اندازی پایگاه داده

### 1.1 ایجاد دیتابیس
```sql
-- اتصال به PostgreSQL
psql -U postgres

-- ایجاد دیتابیس
CREATE DATABASE maxdownloader_cache;

-- ایجاد کاربر
CREATE USER cacheuser WITH PASSWORD 'your_secure_password';

-- اعطای دسترسی‌ها
GRANT ALL PRIVILEGES ON DATABASE maxdownloader_cache TO cacheuser;
```

### 1.2 اجرای Migrations
```bash
# رفتن به پوشه پروژه
cd pro_cache

# ایجاد migrations
alembic init migrations

# ویرایش فایل alembic.ini
# تغییر sqlalchemy.url به:
# postgresql+asyncpg://cacheuser:your_secure_password@localhost/maxdownloader_cache

# ایجاد اولین migration
alembic revision --autogenerate -m "Initial cache tables"

# اجرای migration
alembic upgrade head
```

### 1.3 بررسی جداول
```sql
-- بررسی جداول ایجاد شده
\c maxdownloader_cache
\dt

-- باید این جداول را ببینید:
-- cached_downloads
-- cached_qualities
-- cache_statistics
-- cache_access_logs
-- cache_configuration
```

---

## 🔧 مرحله 2: تنظیم Redis

### 2.1 نصب و راه‌اندازی Redis
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# شروع سرویس
sudo systemctl start redis-server
sudo systemctl enable redis-server

# بررسی وضعیت
redis-cli ping  # باید PONG برگرداند
```

### 2.2 پیکربندی Redis
```bash
# ویرایش فایل تنظیمات
sudo nano /etc/redis/redis.conf

# تغییرات مورد نیاز:
maxmemory 2gb
maxmemory-policy allkeys-lru
appendonly yes
```

---

## 💻 مرحله 3: پیاده‌سازی کد

### 3.1 ساختار فایل‌ها
```
pro_cache/
├── __init__.py
├── config.py              # ایجاد کنید
├── database/
│   ├── __init__.py
│   ├── connection.py      # ایجاد کنید
│   └── models.py         # ✅ موجود
├── services/
│   ├── __init__.py
│   ├── hash_service.py   # ✅ موجود
│   ├── lookup_service.py # ✅ موجود
│   └── storage_service.py # ایجاد کنید
├── handlers/
│   ├── __init__.py
│   └── cache_handler.py  # ✅ موجود
├── keyboards/
│   ├── __init__.py
│   └── cache_keyboards.py # ✅ موجود
└── utils/
    ├── __init__.py
    └── formatters.py      # ✅ موجود
```

### 3.2 ایجاد فایل config.py
```python
# pro_cache/config.py
"""تنظیمات Pro Cache"""

from pydantic import BaseSettings
from typing import Optional


class CacheSettings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://cacheuser:password@localhost/maxdownloader_cache"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_TTL_HOURS: int = 24
    
    # Cache Settings
    MAX_CACHE_SIZE_GB: int = 100
    DEFAULT_TTL_DAYS: int = 30
    CLEANUP_INTERVAL_HOURS: int = 6
    MIN_FILE_SIZE_TO_CACHE_MB: int = 1
    
    # Telegram
    BOT_TOKEN: str
    
    class Config:
        env_file = ".env"


settings = CacheSettings()
```

### 3.3 ایجاد database connection
```python
# pro_cache/database/connection.py
"""مدیریت اتصال به دیتابیس"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

from config import settings


# ایجاد engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=40
)

# ایجاد session factory
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@asynccontextmanager
async def get_async_session():
    """Context manager برای session"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 3.4 ایجاد Storage Service
```python
# pro_cache/services/storage_service.py
"""سرویس ذخیره‌سازی در کش"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import insert

from database.models import CachedDownload, CachedQuality
from database.connection import get_async_session
from services.hash_service import HashService

logger = logging.getLogger(__name__)


class CacheStorageService:
    """سرویس ذخیره محتوا در کش"""
    
    def __init__(self):
        self.hash_service = HashService()
    
    async def store_download(
        self,
        url: str,
        platform: str,
        file_info: Dict[str, Any],
        telegram_file_id: str,
        quality_info: Dict[str, Any]
    ) -> bool:
        """
        ذخیره یک دانلود جدید در کش
        
        Args:
            url: آدرس اصلی
            platform: پلتفرم (youtube, instagram, etc)
            file_info: اطلاعات فایل
            telegram_file_id: شناسه فایل در تلگرام
            quality_info: اطلاعات کیفیت
            
        Returns:
            True در صورت موفقیت
        """
        try:
            # تولید hash
            url_info = self.hash_service.get_url_info(url)
            url_hash = url_info['hash']
            
            async with get_async_session() as session:
                # بررسی وجود قبلی
                existing = await session.get(
                    CachedDownload,
                    {'url_hash': url_hash}
                )
                
                if existing:
                    # فقط کیفیت جدید اضافه کن
                    cache_id = existing.id
                else:
                    # ایجاد رکورد جدید
                    new_cache = CachedDownload(
                        url_hash=url_hash,
                        original_url=url,
                        platform=platform,
                        title=file_info.get('title', 'Unknown'),
                        description=file_info.get('description'),
                        thumbnail_url=file_info.get('thumbnail'),
                        duration=file_info.get('duration'),
                        uploader=file_info.get('uploader'),
                        upload_date=file_info.get('upload_date'),
                        metadata=file_info.get('metadata', {}),
                        expires_at=datetime.utcnow() + timedelta(days=30)
                    )
                    
                    session.add(new_cache)
                    await session.flush()
                    cache_id = new_cache.id
                
                # اضافه کردن کیفیت
                new_quality = CachedQuality(
                    cache_id=cache_id,
                    quality_label=quality_info.get('label', 'Unknown'),
                    format_id=quality_info.get('format_id'),
                    resolution=quality_info.get('resolution'),
                    extension=quality_info.get('ext', 'mp4'),
                    file_size=quality_info.get('filesize', 0),
                    telegram_file_id=telegram_file_id,
                    telegram_file_unique_id=quality_info.get('file_unique_id'),
                    mime_type=quality_info.get('mime_type'),
                    video_codec=quality_info.get('vcodec'),
                    audio_codec=quality_info.get('acodec'),
                    bitrate=quality_info.get('bitrate'),
                    fps=quality_info.get('fps')
                )
                
                session.add(new_quality)
                await session.commit()
                
                logger.info(f"Successfully cached: {url_hash[:8]}... - {quality_info.get('label')}")
                return True
                
        except Exception as e:
            logger.error(f"Error storing to cache: {e}")
            return False
    
    async def mark_cache_invalid(
        self,
        quality_id: int
    ) -> bool:
        """
        علامت‌گذاری یک کش به عنوان نامعتبر
        
        Args:
            quality_id: شناسه کیفیت
            
        Returns:
            True در صورت موفقیت
        """
        try:
            async with get_async_session() as session:
                quality = await session.get(CachedQuality, quality_id)
                if quality:
                    # حذف quality
                    await session.delete(quality)
                    
                    # بررسی آیا کیفیت دیگری وجود دارد
                    cache = await session.get(CachedDownload, quality.cache_id)
                    if cache and len(cache.qualities) == 1:
                        # اگر آخرین کیفیت بود، کل کش را نامعتبر کن
                        cache.is_valid = False
                    
                    await session.commit()
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error marking cache invalid: {e}")
            return False
```

---

## 🔌 مرحله 4: یکپارچه‌سازی با ربات اصلی

### 4.1 اضافه کردن به Bot Loader
```python
# در فایل bot/loader.py پروژه اصلی

from pro_cache.handlers.cache_handler import router as cache_router

# اضافه کردن router
dp.include_router(cache_router)
```

### 4.2 تغییر URL Handler اصلی
```python
# در فایل bot/handlers/download.py

from pro_cache.services.hash_service import HashService
from pro_cache.services.lookup_service import CacheLookupService

async def handle_url(message: Message, state: FSMContext):
    """هندلر اصلی URL با پشتیبانی از کش"""
    
    url = message.text.strip()
    
    # بررسی کش
    hash_service = HashService()
    lookup_service = CacheLookupService()
    
    url_info = hash_service.get_url_info(url)
    cached_content = await lookup_service.find_cached_content(url_info['hash'])
    
    if cached_content:
        # نمایش از کش
        # کد موجود در cache_handler.py
        pass
    else:
        # ادامه فرآیند دانلود عادی
        pass
```

### 4.3 ذخیره در کش پس از دانلود
```python
# در انتهای فرآیند دانلود موفق

from pro_cache.services.storage_service import CacheStorageService

async def after_successful_download(
    url: str,
    file_path: str,
    file_info: dict,
    telegram_file_id: str
):
    """ذخیره فایل دانلود شده در کش"""
    
    storage_service = CacheStorageService()
    
    await storage_service.store_download(
        url=url,
        platform=file_info.get('extractor', 'unknown'),
        file_info=file_info,
        telegram_file_id=telegram_file_id,
        quality_info={
            'label': file_info.get('format_note', 'Default'),
            'format_id': file_info.get('format_id'),
            'resolution': f"{file_info.get('width', 0)}x{file_info.get('height', 0)}",
            'ext': file_info.get('ext', 'mp4'),
            'filesize': file_info.get('filesize', 0),
            'vcodec': file_info.get('vcodec'),
            'acodec': file_info.get('acodec'),
            'fps': file_info.get('fps')
        }
    )
```

---

## 🧪 مرحله 5: تست سیستم

### 5.1 تست پایه
```python
# test_pro_cache.py
import asyncio
from pro_cache.services.hash_service import HashService
from pro_cache.services.lookup_service import CacheLookupService
from pro_cache.services.storage_service import CacheStorageService


async def test_basic_flow():
    # 1. تست Hash Service
    hash_service = HashService()
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    url_info = hash_service.get_url_info(test_url)
    print(f"URL Hash: {url_info['hash']}")
    print(f"Platform: {url_info['platform']}")
    
    # 2. تست Lookup (باید None برگرداند)
    lookup_service = CacheLookupService()
    cached = await lookup_service.find_cached_content(url_info['hash'])
    print(f"Cached (should be None): {cached}")
    
    # 3. تست Storage
    storage_service = CacheStorageService()
    success = await storage_service.store_download(
        url=test_url,
        platform="youtube",
        file_info={
            'title': 'Test Video',
            'duration': 212,
            'uploader': 'Test Channel'
        },
        telegram_file_id="TEST_FILE_ID_123",
        quality_info={
            'label': '1080p',
            'resolution': '1920x1080',
            'ext': 'mp4',
            'filesize': 104857600  # 100MB
        }
    )
    print(f"Storage success: {success}")
    
    # 4. تست Lookup دوباره (باید محتوا برگرداند)
    cached = await lookup_service.find_cached_content(url_info['hash'])
    print(f"Cached after storage: {cached}")
    if cached:
        print(f"Title: {cached.title}")
        print(f"Qualities: {len(cached.qualities)}")


if __name__ == "__main__":
    asyncio.run(test_basic_flow())
```

### 5.2 تست در ربات
1. ارسال یک لینک YouTube به ربات
2. انتخاب کیفیت و دانلود
3. ارسال همان لینک دوباره
4. باید گزینه‌های کش را نشان دهد

---

## 🚨 رفع خطاهای رایج

### خطای اتصال به دیتابیس
```bash
# بررسی سرویس PostgreSQL
sudo systemctl status postgresql

# بررسی دسترسی کاربر
psql -U cacheuser -d maxdownloader_cache
```

### خطای Redis
```bash
# بررسی سرویس Redis
redis-cli ping

# پاک کردن کش Redis
redis-cli FLUSHALL
```

### خطای Import
```bash
# اضافه کردن path
export PYTHONPATH="${PYTHONPATH}:/path/to/pro_cache"
```

---

## 📊 مانیتورینگ و نگهداری

### بررسی حجم کش
```sql
SELECT 
    COUNT(*) as total_files,
    SUM(file_size) / 1024 / 1024 / 1024 as total_gb,
    AVG(access_count) as avg_access
FROM cached_downloads cd
JOIN cached_qualities cq ON cd.id = cq.cache_id
WHERE cd.is_valid = true;
```

### پاکسازی دستی
```sql
-- حذف کش‌های قدیمی‌تر از 30 روز
DELETE FROM cached_downloads
WHERE created_at < CURRENT_DATE - INTERVAL '30 days';

-- حذف کش‌های کم استفاده
DELETE FROM cached_downloads
WHERE access_count < 2
AND created_at < CURRENT_DATE - INTERVAL '7 days';
```

---

## ✅ چک‌لیست نهایی

- [ ] دیتابیس PostgreSQL راه‌اندازی شده
- [ ] Redis نصب و پیکربندی شده
- [ ] جداول دیتابیس ایجاد شده
- [ ] تمام فایل‌های کد ایجاد شده
- [ ] تست‌های پایه اجرا شده
- [ ] یکپارچه‌سازی با ربات اصلی انجام شده
- [ ] حداقل یک فایل با موفقیت کش شده
- [ ] بازیابی از کش تست شده

---

**آماده‌سازی توسط**: تیم توسعه Pro Cache  
**تاریخ**: 1403/03/19  
**نسخه**: 1.0.0