# 🔧 CONFIGURATION & DEPLOYMENT GUIDE

## Phase 1 Configuration (Currently Active)

### 1. Celery Beat Schedule

**فایل:** `/tasks/celery_app.py` یا `settings/celery_config.py`

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    # ... existing tasks ...
    
    # ===== PHASE 1: CACHE MANAGEMENT =====
    
    'cleanup-expired-cache': {
        'task': 'tasks.cache_cleanup_tasks.cleanup_expired_cache',
        'schedule': crontab(hour=2, minute=0),  # 2 AM UTC daily
        'args': (30,)  # Delete entries expired 30+ days ago
    },
    
    'limit-cache-size': {
        'task': 'tasks.cache_cleanup_tasks.limit_cache_size',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
        'args': (5,)  # Keep max 5GB
    },
    
    'cache-statistics': {
        'task': 'tasks.cache_cleanup_tasks.cache_statistics',
        'schedule': crontab(hour=1, minute=0),  # 1 AM UTC daily
    }
}
```

### 2. Cache Settings

**فایل:** `config_simple.py` یا `settings.py`

```python
# Cache Configuration
CACHE_CONFIG = {
    # Expiration
    'expire_days': 30,              # Keep cache 30 days
    'cleanup_schedule': '2 0 * * *',  # 2 AM daily
    
    # Size management
    'max_cache_size_gb': 5,         # Max 5GB total
    'max_single_file_mb': 2000,     # Max 2GB per file
    'lru_check_interval': 6,        # Check every 6 hours
    
    # Performance
    'enable_caching': True,
    'cache_hits_to_consider': 2,    # Cache after 2 hits
    'hash_algorithm': 'sha256',
    
    # Logging
    'log_level': 'INFO',
    'log_cache_hits': True,
    'log_statistics': True
}
```

### 3. Database Connection

**فایل:** `database/connection.py`

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config_simple import settings

# Ensure async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set True for SQL debugging
    pool_size=10,
    max_overflow=20
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

---

## Database Setup

### Create Cache Tables

**Migration Script:**

```bash
# Option 1: Using Alembic
cd /home/reza/Max-Downloader
alembic revision --autogenerate -m "Add cache_downloads table"
alembic upgrade head
```

**Option 2: Manual SQL (if tables don't exist):**

```sql
-- Run in your database
CREATE TABLE IF NOT EXISTS cached_downloads (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    source_url VARCHAR(2048) NOT NULL UNIQUE,
    file_hash VARCHAR(64) UNIQUE,
    telegram_file_id VARCHAR(255) UNIQUE NOT NULL,
    media_title VARCHAR(500),
    file_size BIGINT,
    quality VARCHAR(100),
    format_codec VARCHAR(50),
    format_container VARCHAR(20),
    resolution_width INT,
    resolution_height INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    download_count INT DEFAULT 0,
    source_platform VARCHAR(50),
    
    INDEX idx_url (source_url),
    INDEX idx_hash (file_hash),
    INDEX idx_created (created_at),
    INDEX idx_expires (expires_at)
);

-- For queue management (Phase 2)
CREATE TABLE IF NOT EXISTS download_queue (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    url VARCHAR(2048) NOT NULL,
    priority INT DEFAULT 2,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
);
```

---

## Environment Setup

### 1. Install Dependencies

```bash
cd /home/reza/Max-Downloader

# Core dependencies
pip install -r requirements.txt

# For Celery beat
pip install celery[redis]
pip install redis

# For parallel downloads (Phase 2)
pip install concurrent-futures  # Usually built-in

# For compression (Phase 4)
pip install ffmpeg-python

# For monitoring (Phase 5)
pip install psutil

# For testing
pip install pytest pytest-asyncio pytest-cov
```

### 2. Redis Setup (Optional but Recommended)

```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
redis-server

# Test connection
redis-cli ping
# Output: PONG ✅
```

### 3. Celery Worker Configuration

**فایل:** `/tasks/celery_app.py`

```python
from celery import Celery
from config_simple import settings

app = Celery('max_downloader')

# Configure broker (RabbitMQ or Redis)
app.conf.broker_url = settings.CELERY_BROKER_URL or 'redis://localhost:6379/0'
app.conf.result_backend = settings.CELERY_RESULT_BACKEND or 'redis://localhost:6379/1'

# Other config
app.conf.task_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.result_serializer = 'json'
app.conf.timezone = 'UTC'
app.conf.enable_utc = True

# Autodiscover tasks
app.autodiscover_tasks(['tasks'])
```

### 4. Start Celery Worker

```bash
# Terminal 1: Start Celery Worker
cd /home/reza/Max-Downloader
celery -A tasks.celery_app worker --loglevel=info

# Terminal 2: Start Celery Beat
cd /home/reza/Max-Downloader
celery -A tasks.celery_app beat --loglevel=info

# Terminal 3: Start Bot
python main.py
```

---

## Debugging Guide

### 1. Check Cache Table

```python
from database.repositories.cached_download_repo import CachedDownloadRepository
from database.connection import AsyncSessionLocal

async def debug_cache():
    async with AsyncSessionLocal() as session:
        repo = CachedDownloadRepository(session)
        
        # Get all cached items
        all_items = await repo.get_all()
        print(f"📦 Total cached items: {len(all_items)}")
        
        for item in all_items:
            print(f"  ✅ {item.source_url[:50]}... → {item.file_size/1024/1024:.1f}MB")

# Run: asyncio.run(debug_cache())
```

### 2. Monitor Celery Tasks

```bash
# List active tasks
celery -A tasks.celery_app inspect active

# Get task stats
celery -A tasks.celery_app inspect stats

# Monitor in real-time
watch -n 1 'celery -A tasks.celery_app inspect active'
```

### 3. Check Logs

```bash
# Bot logs
tail -f logs/bot.log

# Celery worker logs
tail -f logs/celery_worker.log

# Database logs (if enabled)
grep "CACHE" logs/*.log | head -20
```

### 4. Common Issues

**Issue:** Celery tasks not running
```bash
# Solution: Check Redis connection
redis-cli ping

# Or use RabbitMQ
service rabbitmq-server status
```

**Issue:** Cache not working
```bash
# Check database connection
python -c "from database.connection import engine; print('✅ DB Connected')"

# Check table exists
sqlite3 your_db.db ".tables" | grep cached_downloads
```

**Issue:** Memory issues
```bash
# Monitor memory
free -h

# Check cache size
SELECT SUM(file_size) / 1024 / 1024 / 1024 as total_gb FROM cached_downloads;

# Clear old cache manually
DELETE FROM cached_downloads WHERE expires_at < NOW();
```

---

## Performance Tuning

### 1. Database Connection Pool

```python
# In connection.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # Increase if many concurrent
    max_overflow=40,        # Max connection overflow
    pool_pre_ping=True      # Test connection before use
)
```

### 2. Cache Tuning

```python
# In cache_service.py
# Adjust based on your storage
MAX_CACHE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
EXPIRE_DAYS = 30
CLEANUP_INTERVAL = 6  # hours
```

### 3. Celery Tuning

```python
# In celery_app.py
app.conf.task_soft_time_limit = 300  # 5 min
app.conf.task_time_limit = 600  # 10 min
app.conf.worker_prefetch_multiplier = 4
app.conf.worker_max_tasks_per_child = 1000
```

---

## Deployment Checklist

```
Pre-Deployment:
☐ Phase 1 tests pass (pytest)
☐ Database tables created
☐ Celery worker tested
☐ Redis/Broker running
☐ Configuration reviewed
☐ Logs configured
☐ Backups created

Deployment:
☐ Run migrations (if any)
☐ Start Celery worker
☐ Start Celery beat
☐ Start bot
☐ Monitor logs
☐ Test cache functionality
☐ Verify cleanup tasks running

Post-Deployment:
☐ Monitor performance
☐ Check error rates
☐ Verify cache hits
☐ Monitor resource usage
☐ Set up alerts
☐ Regular backups
```

---

## Monitoring & Alerts

### 1. Cache Hit Rate

```python
# Log periodically
async def log_cache_stats():
    stats = await cache_service.get_cache_stats(session)
    hit_rate = (stats['hits'] / stats['total_requests']) * 100 if stats['total_requests'] > 0 else 0
    
    logger.info(f"[STATS] Cache hit rate: {hit_rate:.1f}%")
    logger.info(f"[STATS] Cached items: {stats['total_items']}")
    logger.info(f"[STATS] Total size: {stats['total_size_gb']:.2f}GB")
    
    # Alert if too low
    if hit_rate < 10:
        logger.warning(f"⚠️ Low cache hit rate: {hit_rate:.1f}%")
```

### 2. Task Monitoring

```bash
# Celery Flower (Web UI for monitoring)
pip install flower
celery -A tasks.celery_app flower

# Open http://localhost:5555
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Cache not persistent | Check DB connection, table exists, filesystem space |
| Cleanup not running | Check Celery beat, Redis broker, task imports |
| High memory usage | Reduce MAX_CACHE_SIZE, enable LRU cleanup |
| Slow downloads | Phase 1 cache ok, start Phase 2 (parallel) |
| Database locked | Too many connections - increase pool_size |

---

## Next Steps

### Phase 2 Preparation
```
☐ Review PHASE_2_QUICK_START.md
☐ Plan parallel download architecture
☐ Create test suite template
☐ Design queue database schema
☐ Plan handler modifications
```

### Phase 3+ Preparation
```
☐ FFmpeg installation for Phase 4
☐ Stream architecture design for Phase 3
☐ Priority queue implementation for Phase 5
```

---

**Current Status:** Phase 1 ✅ Configured & Ready
**Configuration Level:** Production-Ready
**Monitoring:** Enabled ✅
