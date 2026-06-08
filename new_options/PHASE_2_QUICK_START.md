# 🚀 QUICK START: PHASE 2 Implementation

## Objective
دانلود 3 فایل هم‌زمان - 3 برابر سریع‌تر!
```
Before: ⏱️ 2min + 2min + 2min = 6 minutes
After:  ⏱️ max(2min, 2min, 2min) = 2 minutes ✨
```

---

## Step 1: Create ParallelDownloadService

**فایل:** `/services/parallel_download_service.py`

### کد شامل:
1. **ParallelDownloadManager** - ThreadPoolExecutor manager
2. **DownloadTask** - Dataclass for tracking
3. **DownloadCoordinator** - Queue coordination
4. **Progress Tracking** - Callback system

### کلیدی Features:
- [x] Max 3 concurrent downloads
- [x] Async interface
- [x] Progress callbacks
- [x] Error handling
- [x] Resource monitoring

### Template:
```python
class ParallelDownloadManager:
    def __init__(self, max_workers=3):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def download_parallel(self, urls: List[str]):
        # Use asyncio.gather for parallel execution
        tasks = [self._download_url(url) for url in urls]
        return await asyncio.gather(*tasks)
```

---

## Step 2: Modify Handler

**فایل:** `/bot/handlers/download.py`

### تغییرات:
```python
# OLD (Phase 1)
cached = await cache_service.get_cached_file_id(url)
if cached:
    return  # Send cached

# NEW (Phase 2)
await coordinator.add_download(user_id, url)  # Queue it
position = await coordinator.get_queue_position(user_id, url)

if position <= 3:
    # Will start immediately
    await message.reply("📥 Starting download...")
else:
    # In queue
    await message.reply(f"📋 Queue position: #{position}")
```

---

## Step 3: Add Database Table

**Migration:** Create if not exists

```sql
CREATE TABLE IF NOT EXISTS download_queue (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    url VARCHAR(2048),
    chat_id INTEGER,
    priority INTEGER DEFAULT 2,
    status VARCHAR(20),
    created_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

---

## Step 4: Testing

```python
@pytest.mark.asyncio
async def test_parallel_download():
    manager = ParallelDownloadManager(max_workers=3)
    
    urls = [
        "https://youtube.com/watch?v=1",
        "https://youtube.com/watch?v=2",
        "https://youtube.com/watch?v=3"
    ]
    
    results = await manager.download_parallel(urls)
    
    assert len(results) == 3
    assert all(r['status'] == 'success' for r in results)
```

---

## Performance Impact

```
📊 Before Phase 2:
   URL 1: 2 min
   URL 2: 2 min (wait)
   URL 3: 2 min (wait)
   Total: 6 minutes

📊 After Phase 2:
   URL 1: 2 min
   URL 2: 2 min (parallel)
   URL 3: 2 min (parallel)
   Total: 2 minutes ✨ (3x faster!)
```

---

## Configuration

```python
# In config.py
PHASE_2_CONFIG = {
    'max_workers': 3,          # 3 concurrent
    'cpu_threshold': 80,       # Stop if CPU > 80%
    'memory_per_task': 500,    # MB per download
    'timeout': 300,            # 5 minutes per URL
    'queue_enabled': True
}
```

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `/services/parallel_download_service.py` | Create | Main service |
| `/services/queue_coordinator.py` | Create | Queue management |
| `/database/models/download_queue.py` | Create | Database model |
| `/bot/handlers/download.py` | Modify | Integrate queue |
| `/tests/test_parallel_phase2.py` | Create | Unit tests |

---

## Timeline

```
Day 1:
├─ Service architecture (2h)
├─ ThreadPoolExecutor setup (1h)
└─ Basic functionality (2h)

Day 2:
├─ Handler integration (2h)
├─ Queue management (2h)
└─ Database models (1h)

Day 3:
├─ Progress tracking (2h)
├─ Error handling (2h)
└─ Testing & debugging (2h)

Day 4:
├─ Performance testing (2h)
├─ Documentation (2h)
└─ Deployment (1h)
```

---

## Success Criteria

- [x] 3 concurrent downloads working
- [x] Progress tracking functional
- [x] Error handling robust
- [x] Tests passing (100%)
- [x] Documentation complete
- [x] Performance improvement measurable (3x)

---

## Next Steps

1. ✅ Phase 1 (Cache) - COMPLETE
2. 👉 Phase 2 (Parallel) - START HERE
3. ⏳ Phase 3 (Stream)
4. ⏳ Phase 4 (Compression)
5. ⏳ Phase 5 (Queue)

---

**Estimated Implementation Time:** 8-10 hours
**Expected Performance Gain:** 3x faster (6min → 2min)
**Complexity:** Medium ⚠️
