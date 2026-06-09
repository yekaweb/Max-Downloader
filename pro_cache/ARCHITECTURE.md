# 🏗️ Pro Cache - مستندات معماری سیستم

## 📐 معماری کلی (High-Level Architecture)

### نمای کلی سیستم

```
┌─────────────────────────────────────────────────────────────────┐
│                         Max-Downloader Bot                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     │
│  │   Telegram  │     │   Download  │     │    Admin    │     │
│  │   Handler   │────▶│   Module    │     │    Panel    │     │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘     │
│         │                    │                    │            │
│         ▼                    ▼                    ▼            │
│  ╔═══════════════════════════════════════════════════════╗    │
│  ║                    Pro Cache Layer                     ║    │
│  ╠═══════════════════════════════════════════════════════╣    │
│  ║  ┌───────────┐  ┌───────────┐  ┌───────────┐         ║    │
│  ║  │   Hash    │  │   Cache   │  │  Cleanup  │         ║    │
│  ║  │  Engine   │  │  Lookup   │  │  Service  │         ║    │
│  ║  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘         ║    │
│  ║        │              │              │                ║    │
│  ║        ▼              ▼              ▼                ║    │
│  ║  ┌─────────────────────────────────────────┐         ║    │
│  ║  │         Cache Repository Layer          │         ║    │
│  ║  └─────────────────┬───────────────────────┘         ║    │
│  ╚════════════════════╪══════════════════════════════════╝    │
│                       │                                        │
│         ┌─────────────┴─────────────┐                         │
│         ▼                           ▼                         │
│  ┌─────────────┐            ┌─────────────┐                  │
│  │ PostgreSQL  │            │    Redis    │                  │
│  │  Database   │            │    Cache    │                  │
│  └─────────────┘            └─────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Diagram

### 1. Cache Hit Flow (موفق)

```
User ─────► URL Input ─────► Hash Generation ─────► Cache Lookup
                                                           │
                                                           ▼
                                                     Found in Cache
                                                           │
                                                           ▼
                                                    Load Qualities
                                                           │
                                                           ▼
                                                    Display Options
                                                           │
                                                           ▼
User Selects ◄───── Send File (0.5s) ◄───── Get File ID ◄─┘
```

### 2. Cache Miss Flow (ناموفق)

```
User ─────► URL Input ─────► Hash Generation ─────► Cache Lookup
                                                           │
                                                           ▼
                                                    Not in Cache
                                                           │
                                                           ▼
                                                   Start Download
                                                           │
                                                           ▼
                                                   Process Video
                                                           │
                                                           ▼
                                                  Upload to Telegram
                                                           │
                                                           ▼
                                                  Store in Cache
                                                           │
                                                           ▼
User Receives ◄────────────── Send to User ◄──────────────┘
```

## 🗄️ Database Schema

### جدول اصلی: cached_downloads

```sql
CREATE TABLE cached_downloads (
    id SERIAL PRIMARY KEY,
    url_hash VARCHAR(64) UNIQUE NOT NULL,
    original_url VARCHAR(500) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    thumbnail_url VARCHAR(500),
    duration INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    is_valid BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,
    metadata JSONB,
    
    -- Indexes
    INDEX idx_url_hash (url_hash),
    INDEX idx_platform (platform),
    INDEX idx_expires_at (expires_at),
    INDEX idx_access_count (access_count)
);
```

### جدول کیفیت‌ها: cached_qualities

```sql
CREATE TABLE cached_qualities (
    id SERIAL PRIMARY KEY,
    cache_id INTEGER REFERENCES cached_downloads(id) ON DELETE CASCADE,
    quality_label VARCHAR(50) NOT NULL,
    format_id VARCHAR(50),
    resolution VARCHAR(20),
    file_size BIGINT,
    telegram_file_id VARCHAR(255) UNIQUE NOT NULL,
    mime_type VARCHAR(50),
    codec VARCHAR(50),
    bitrate INTEGER,
    fps INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    download_count INTEGER DEFAULT 0,
    
    -- Indexes
    INDEX idx_cache_id (cache_id),
    INDEX idx_quality_label (quality_label),
    INDEX idx_file_id (telegram_file_id)
);
```

### جدول آمار: cache_statistics

```sql
CREATE TABLE cache_statistics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    total_hits INTEGER DEFAULT 0,
    total_misses INTEGER DEFAULT 0,
    total_saves BIGINT DEFAULT 0,  -- bytes saved
    unique_users INTEGER DEFAULT 0,
    avg_response_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    UNIQUE INDEX idx_date (date)
);
```

## 🔧 Component Details

### 1. Hash Engine Component

```python
class HashEngine:
    """
    مسئول تولید hash یکتا برای هر URL
    
    ویژگی‌ها:
    - نرمال‌سازی URL قبل از hash
    - حذف پارامترهای غیرضروری
    - پشتیبانی از URL های کوتاه شده
    - سازگاری با پلتفرم‌های مختلف
    """
    
    def __init__(self):
        self.normalizers = {
            'youtube': YouTubeNormalizer(),
            'instagram': InstagramNormalizer(),
            'tiktok': TikTokNormalizer(),
            'twitter': TwitterNormalizer()
        }
    
    def generate_hash(self, url: str) -> str:
        # 1. تشخیص پلتفرم
        platform = self.detect_platform(url)
        
        # 2. نرمال‌سازی URL
        normalized_url = self.normalizers[platform].normalize(url)
        
        # 3. تولید SHA-256 hash
        return hashlib.sha256(normalized_url.encode()).hexdigest()
```

### 2. Cache Lookup Service

```python
class CacheLookupService:
    """
    مدیریت جستجو و بازیابی از کش
    
    ویژگی‌ها:
    - جستجوی سریع با استفاده از index
    - بررسی validity و expiration
    - بروزرسانی آمار دسترسی
    - مدیریت cache warming
    """
    
    async def find_cached_content(self, url_hash: str) -> Optional[CachedContent]:
        # 1. جستجو در Redis (سطح اول)
        redis_result = await self.redis_client.get(f"cache:{url_hash}")
        if redis_result:
            return CachedContent.from_redis(redis_result)
        
        # 2. جستجو در PostgreSQL (سطح دوم)
        db_result = await self.db.query(
            "SELECT * FROM cached_downloads WHERE url_hash = %s AND is_valid = TRUE",
            url_hash
        )
        
        if db_result:
            # 3. گرم کردن Redis cache
            await self.warm_redis_cache(url_hash, db_result)
            return CachedContent.from_db(db_result)
        
        return None
```

### 3. Storage Service

```python
class CacheStorageService:
    """
    ذخیره‌سازی محتوا در کش
    
    ویژگی‌ها:
    - ذخیره atomic با transaction
    - مدیریت روابط بین جداول
    - تولید metadata خودکار
    - محاسبه expiration time
    """
    
    async def store_download(
        self, 
        url: str, 
        file_info: dict, 
        telegram_file_id: str
    ) -> bool:
        async with self.db.transaction() as tx:
            # 1. ذخیره اطلاعات اصلی
            cache_id = await self._store_main_info(tx, url, file_info)
            
            # 2. ذخیره کیفیت
            await self._store_quality(tx, cache_id, file_info, telegram_file_id)
            
            # 3. بروزرسانی آمار
            await self._update_statistics(tx)
            
            # 4. کش کردن در Redis
            await self._cache_in_redis(url_hash, cache_id)
            
            return True
```

### 4. Cleanup Service

```python
class CleanupService:
    """
    پاکسازی و مدیریت حافظه کش
    
    ویژگی‌ها:
    - اجرای دوره‌ای (هر 6 ساعت)
    - استراتژی LRU برای حذف
    - محدودیت حجم کلی
    - گزارش‌دهی آماری
    """
    
    async def cleanup(self):
        # 1. حذف expired items
        deleted_expired = await self._cleanup_expired()
        
        # 2. بررسی حجم کلی
        if await self._is_over_limit():
            deleted_lru = await self._cleanup_lru()
        
        # 3. پاکسازی orphaned records
        deleted_orphans = await self._cleanup_orphans()
        
        # 4. گزارش نهایی
        await self._report_cleanup_stats(
            expired=deleted_expired,
            lru=deleted_lru,
            orphans=deleted_orphans
        )
```

## 🔌 Integration Points

### 1. با سیستم اصلی Bot

```python
# در فایل bot/handlers/download.py

from pro_cache import CacheManager

class DownloadHandler:
    def __init__(self):
        self.cache_manager = CacheManager()
    
    async def handle_url(self, message: Message):
        url = message.text
        
        # بررسی کش
        cached_content = await self.cache_manager.lookup(url)
        
        if cached_content:
            # نمایش گزینه‌های کش
            await self.show_cache_options(message, cached_content)
        else:
            # شروع دانلود جدید
            await self.start_fresh_download(message, url)
```

### 2. با ماژول‌های دانلود

```python
# Decorator برای کش خودکار

from pro_cache import cache_result

class YouTubeDownloader:
    @cache_result(expire_after=timedelta(days=30))
    async def download(self, url: str, quality: str) -> DownloadResult:
        # منطق دانلود
        result = await self._download_video(url, quality)
        return result
```

### 3. با پنل ادمین

```python
# API endpoints برای مدیریت کش

@router.get("/cache/stats")
async def get_cache_statistics():
    return {
        "total_size": await cache.get_total_size(),
        "total_items": await cache.get_item_count(),
        "hit_rate": await cache.get_hit_rate(),
        "saved_bandwidth": await cache.get_saved_bandwidth()
    }

@router.delete("/cache/clear")
async def clear_cache(older_than: Optional[int] = None):
    if older_than:
        deleted = await cache.clear_older_than(days=older_than)
    else:
        deleted = await cache.clear_all()
    
    return {"deleted_items": deleted}
```

## 🔐 Security Considerations

### 1. Data Validation
- همه URL ها قبل از پردازش validate می‌شوند
- محدودیت طول URL: 500 کاراکتر
- فیلتر کردن کاراکترهای خطرناک

### 2. Access Control
- فقط ادمین‌ها می‌توانند کش را پاک کنند
- محدودیت rate برای جلوگیری از سوءاستفاده
- لاگ کردن تمام دسترسی‌ها

### 3. Data Privacy
- عدم ذخیره اطلاعات شخصی کاربران
- رمزنگاری file_id ها در دیتابیس
- حذف خودکار داده‌های قدیمی

## ⚡ Performance Optimizations

### 1. Database
- استفاده از Connection Pooling
- Prepared Statements برای query های تکراری
- Batch operations برای insert/update
- Partitioning برای جداول بزرگ

### 2. Caching Strategy
```
┌─────────────┐
│   Browser   │ ◄── Service Worker Cache
└──────┬──────┘
       │
┌──────▼──────┐
│  CDN Cache  │ ◄── 1 hour TTL
└──────┬──────┘
       │
┌──────▼──────┐
│ Redis Cache │ ◄── 24 hours TTL
└──────┬──────┘
       │
┌──────▼──────┐
│  Database   │ ◄── 30 days TTL
└─────────────┘
```

### 3. Query Optimization
```sql
-- استفاده از Materialized Views برای آمار
CREATE MATERIALIZED VIEW cache_stats_daily AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_requests,
    SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as hits,
    AVG(response_time) as avg_response_time
FROM cache_access_log
GROUP BY DATE(created_at);

-- Refresh هر ساعت
REFRESH MATERIALIZED VIEW cache_stats_daily;
```

## 📊 Monitoring & Observability

### 1. Metrics Collection
```python
# Prometheus metrics
cache_hits = Counter('cache_hits_total', 'Total cache hits')
cache_misses = Counter('cache_misses_total', 'Total cache misses')
cache_size = Gauge('cache_size_bytes', 'Current cache size')
response_time = Histogram('cache_response_seconds', 'Response time')
```

### 2. Logging Structure
```json
{
    "timestamp": "2024-01-01T12:00:00Z",
    "level": "INFO",
    "service": "pro_cache",
    "event": "cache_hit",
    "url_hash": "abc123...",
    "platform": "youtube",
    "quality": "1080p",
    "response_time_ms": 245,
    "user_id": "123456",
    "saved_bytes": 104857600
}
```

### 3. Alerts Configuration
- Cache hit rate < 50% → Warning
- Database connection errors → Critical
- Redis memory > 80% → Warning
- Cleanup failures → Error

## 🔄 Deployment Architecture

```
┌─────────────────────────────────────────────┐
│              Load Balancer                  │
└───────────────┬─────────────────────────────┘
                │
    ┌───────────┴───────────┬───────────┐
    ▼                       ▼           ▼
┌────────┐            ┌────────┐   ┌────────┐
│ Node 1 │            │ Node 2 │   │ Node 3 │
│  Bot   │            │  Bot   │   │  Bot   │
└───┬────┘            └───┬────┘   └───┬────┘
    │                     │             │
    └─────────┬───────────┴─────────────┘
              ▼
    ┌─────────────────┐
    │  Redis Cluster  │
    │   (3 nodes)     │
    └─────────────────┘
              │
    ┌─────────▼─────────┐
    │   PostgreSQL     │
    │  (Primary-Replica)│
    └───────────────────┘
```

## 🛠️ Development Guidelines

### 1. Code Structure
```
pro_cache/
├── core/
│   ├── hash_engine.py      # Hash generation logic
│   ├── validators.py       # URL validation
│   └── exceptions.py       # Custom exceptions
├── services/
│   ├── lookup_service.py   # Cache lookup
│   ├── storage_service.py  # Cache storage
│   └── cleanup_service.py  # Maintenance
├── models/
│   ├── cache_models.py     # SQLAlchemy models
│   └── redis_models.py     # Redis data structures
└── utils/
    ├── metrics.py          # Monitoring utilities
    └── helpers.py          # Common helpers
```

### 2. Testing Strategy
- Unit tests: تست تمام متدها به صورت جداگانه
- Integration tests: تست فرآیند end-to-end
- Load tests: شبیه‌سازی 10,000 کاربر همزمان
- Chaos testing: تست با قطع اتصالات

### 3. Best Practices
- استفاده از Type Hints در تمام کدها
- Docstring برای تمام کلاس‌ها و متدها
- Error handling در تمام سطوح
- Async/await برای تمام I/O operations

---

**نسخه**: 1.0.0  
**آخرین بروزرسانی**: 1403/03/19  
**نویسنده**: تیم معماری Max-Downloader