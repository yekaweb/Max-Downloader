# 🏗️ Architecture & System Design

## نمودار معماری سیستم

### معماری کنونی (Current)
```
┌─────────────────────────────────────────────────────┐
│                    Telegram Bot                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐    ┌──────────────┐              │
│  │   Handler    │───▶│  Downloader  │              │
│  │ (URL Input)  │    │  (yt-dlp)    │              │
│  └──────────────┘    └──────────────┘              │
│         │                    │                      │
│         │                    ▼                      │
│         │            ┌──────────────┐              │
│         │            │  File Saved  │              │
│         │            │  (temp dir)  │              │
│         │            └──────────────┘              │
│         │                    │                      │
│         └────────────────────┼─────────────────┐   │
│                              ▼                 ▼   │
│                      ┌──────────────┐  ┌──────────┐│
│                      │ Uploader     │  │ Delete   ││
│                      │ (send file)  │  │ (cleanup)││
│                      └──────────────┘  └──────────┘│
│                                                      │
└─────────────────────────────────────────────────────┘

مشکلات:
❌ بدون caching
❌ دانلود ترتیبی
❌ آپلود بدون buffer
❌ بدون کمپرس
❌ بدون queue management
```

### معماری جدید (Enhanced - After All Phases)
```
┌──────────────────────────────────────────────────────────┐
│                    Telegram Bot (v2.0)                    │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Cache System (Phase 1)                 │ │
│  │  ┌──────────────┐      ┌─────────────────────┐    │ │
│  │  │  Check Cache │──────▶│  Found in DB? Yes  │    │ │
│  │  │  (URL input) │      │  Send Telegram ID  │    │ │
│  │  └──────────────┘      │  ⏱️ 0.5 seconds     │    │ │
│  │         │              └─────────────────────┘    │ │
│  │      No │                                         │ │
│  │         ▼                                         │ │
│  └─────────────────────────────────────────────────────┘ │
│         │                                               │
│         ▼                                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │         Priority Queue (Phase 5)                    │ │
│  │  ┌──────────────────────────────────┐             │ │
│  │  │ Check Resource Status            │             │ │
│  │  │ CPU, Memory, Bandwidth           │             │ │
│  │  └──────────────────────────────────┘             │ │
│  │         │                                          │ │
│  │         ▼                                          │ │
│  │  ┌──────────────────────────────────┐             │ │
│  │  │ Assign Priority & Position       │             │ │
│  │  │ Premium: High | Free: Normal    │             │ │
│  │  └──────────────────────────────────┘             │ │
│  │         │                                          │ │
│  │         ▼                                          │ │
│  │  ┌──────────────────────────────────┐             │ │
│  │  │ Notify User of Queue Position    │             │ │
│  │  │ Position: #2 | ETA: 10 minutes  │             │ │
│  │  └──────────────────────────────────┘             │ │
│  └─────────────────────────────────────────────────────┘ │
│         │                                               │
│         ▼                                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │      Parallel Download (Phase 2)                    │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐            │ │
│  │  │Download │  │Download │  │Download │            │ │
│  │  │File #1  │  │File #2  │  │File #3  │            │ │
│  │  │ 33%     │  │ 50%     │  │ 20%     │            │ │
│  │  └─────────┘  └─────────┘  └─────────┘            │ │
│  │  ThreadPool (max_workers=3)                        │ │
│  └─────────────────────────────────────────────────────┘ │
│         │                                               │
│         ▼                                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │        Compression (Phase 4)                        │ │
│  │  ┌──────────────────────────────────┐             │ │
│  │  │ Input: 100MB (1080p video)      │             │ │
│  │  │ FFmpeg H.264 Compression        │             │ │
│  │  │ CRF: 23 (quality), Preset: fast │             │ │
│  │  │ Output: 60MB (40% reduction)    │             │ │
│  │  └──────────────────────────────────┘             │ │
│  └─────────────────────────────────────────────────────┘ │
│         │                                               │
│         ▼                                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │       Stream Upload (Phase 3)                       │ │
│  │  ┌─────────────────────────────────┐              │ │
│  │  │  Reading Chunks                 │              │ │
│  │  │  ┌──────┐ ┌──────┐ ┌──────┐    │              │ │
│  │  │  │ 5MB  │ │ 5MB  │ │ 5MB  │    │              │ │
│  │  │  └──────┘ └──────┘ └──────┘    │              │ │
│  │  └─────────────────────────────────┘              │ │
│  │              │                                    │ │
│  │              ▼                                    │ │
│  │  ┌─────────────────────────────────┐              │ │
│  │  │  Telegram Upload (Parallel)     │              │ │
│  │  │  ┌──────┐ ┌──────┐ ┌──────┐    │              │ │
│  │  │  │Upload│ │Upload│ │Upload│    │              │ │
│  │  │  └──────┘ └──────┘ └──────┘    │              │ │
│  │  └─────────────────────────────────┘              │ │
│  │  (50% faster than sequential)                    │ │
│  └─────────────────────────────────────────────────────┘ │
│         │                                               │
│         ▼                                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │      Cache Saving & Cleanup                        │ │
│  │  ┌──────────────────────────────────┐             │ │
│  │  │ Save: URL + Telegram File ID     │             │ │
│  │  │ To: SQLite Database              │             │ │
│  │  │ Expire: 30 days auto-cleanup     │             │ │
│  │  └──────────────────────────────────┘             │ │
│  │  ┌──────────────────────────────────┐             │ │
│  │  │ Delete temp files                │             │ │
│  │  │ Update user stats                │             │ │
│  │  └──────────────────────────────────┘             │ │
│  └─────────────────────────────────────────────────────┘ │
│         │                                               │
│         ▼                                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │         Send to User                                │ │
│  │  Document: 60MB (compressed)                       │ │
│  │  Caption: Download completed! ✅                   │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                            │
└──────────────────────────────────────────────────────────┘

✅ تمام مشکلات حل شدند!
```

---

## 📊 Data Flow Diagrams

### Phase 1: Caching
```
User URL
   │
   ▼
┌─────────────────┐
│ Check DB Cache  │
└─────────────────┘
   │          │
   │ Found    │ Not Found
   │          │
   ▼          ▼
[Send]    [Download]
(0.5s)     (2min)
   │          │
   │          ▼
   │      ┌─────────────┐
   │      │ Save to DB  │
   │      └─────────────┘
   │          │
   └──────────▼
        [Send]
       (2min)
```

### Phase 2: Parallel Downloads
```
URLs (3 items)
   │
   ▼
┌──────────────────┐
│ Thread Pool (3)  │
│                  │
│ ┌──┐ ┌──┐ ┌──┐  │
│ │1 │ │2 │ │3 │  │
│ └──┘ └──┘ └──┘  │
│ Download        │
│ Parallel        │
└──────────────────┘
   │
   ▼
[Results]
(2min for 3 files)
```

### Phase 3: Stream Upload
```
File Downloaded
   │
   ▼
┌──────────────────┐
│ Read in Chunks   │ (5MB each)
│ ┌──┐ ┌──┐ ┌──┐  │
│ │ 1│ │ 2│ │ 3│  │
│ └──┘ └──┘ └──┘  │
└──────────────────┘
   │
   ├──────┬────────┬──────┐
   ▼      ▼        ▼      ▼
[Buffer Management]
   │
   ├──────┬────────┬──────┐
   ▼      ▼        ▼      ▼
[Upload to Telegram]
(Parallel)
   │
   ▼
[File Sent]
(50% faster)
```

### Phase 4: Compression
```
Downloaded File (100MB)
   │
   ▼
┌────────────────────┐
│ Analyze Format     │
│ Platform: Telegram │
│ Size > 50MB?       │
└────────────────────┘
   │
   ▼
┌────────────────────┐
│ FFmpeg Compression │
│ H.264 + CRF 23     │
│ fast preset        │
└────────────────────┘
   │
   ▼
[Output: 60MB]
(40% reduction)
   │
   ▼
[Upload]
(faster)
```

### Phase 5: Queue Management
```
┌──────────────────────────┐
│ Resource Monitor         │
│ CPU | Memory | Bandwidth │
└──────────────────────────┘
   │
   ▼
┌──────────────────────────┐
│ Priority Queue           │
│ ┌────────────────────┐   │
│ │ Premium: HIGH      │ 1 │
│ │ Users: NORMAL      │ 2 │
│ │ Free: LOW          │ 3 │
│ └────────────────────┘   │
└──────────────────────────┘
   │
   ├─ Active: max 3 concurrent
   ├─ Queued: waiting
   └─ Completed: removed
   │
   ▼
┌──────────────────────────┐
│ Notify User              │
│ Position: #2             │
│ ETA: 10 minutes          │
└──────────────────────────┘
```

---

## 🗄️ Database Schema

### CachedDownload Model
```
Table: cached_downloads

Columns:
├── id (Primary Key)
├── url (String, UNIQUE, INDEX)
├── file_hash (String, INDEX)
├── telegram_file_id (String)
├── media_title (String)
├── file_size (Integer)
├── quality (String)
├── format_type (String)
├── duration (Integer)
├── thumb_url (String)
├── cached_at (DateTime, INDEX)
├── last_used (DateTime)
├── expire_at (DateTime)
├── is_valid (Boolean)
└── usage_count (Integer)

Indexes:
├── idx_url (for fast lookup)
├── idx_file_hash (for deduplication)
└── idx_cached_at (for cleanup)

Constraints:
├── UNIQUE(url)
├── FOREIGN KEY cascade on delete
└── AUTO-CLEANUP after 30 days
```

---

## 🔄 Process Flows

### Download with Cache (New)
```
Request → Check Cache → Found? 
                           ├─ YES → Send (0.5s) ✨
                           └─ NO → Download → Compress → Upload → Cache
```

### Parallel Download
```
Requests (3) → ThreadPool → Concurrent execution → Combine results
              (max 3)       (2min instead of 6min) → Send to user
```

### Stream Upload
```
Download → Read Chunks → Upload Parallel → Manage Buffer → Done
(2min)     (5MB each)   (at same time)   (50% faster)
```

### Complete Flow (All Phases)
```
URL Input
   ↓
Cache Check ──[HIT]──→ Send (0.5s) ✨
   ↓
[MISS] → Priority Queue
   ↓
Wait for Resources
   ↓
Parallel Download (1 of 3)
   ↓
Compression (40% reduction)
   ↓
Stream Upload (50% faster)
   ↓
Cache Save
   ↓
Cleanup
   ↓
Send to User ✅
```

---

## ⚙️ System Components

### Services
```
services/
├── cache_service.py
│   ├── calculate_file_hash()
│   ├── get_cached_file_id()
│   └── save_to_cache()
│
├── parallel_download_service.py
│   ├── ParallelDownloadManager
│   ├── DownloadCoordinator
│   └── download_parallel()
│
├── stream_upload_service.py
│   ├── StreamUploadService
│   ├── BufferManager
│   └── stream_upload_to_telegram()
│
├── compression_service.py
│   ├── CompressionService
│   ├── AdaptiveCompression
│   └── compress_video/audio()
│
└── queue_service.py
    ├── PriorityQueueManager
    ├── ResourceManager
    └── UnifiedDownloadOrchestrator
```

### Database
```
database/
├── models/
│   └── cached_download.py
│       └── CachedDownload
│
└── repositories/
    └── cached_download_repo.py
        └── CachedDownloadRepository
```

### Handlers
```
bot/handlers/
├── download.py (Modified)
│   └── handle_url() [+ Cache Check]
│
├── download_complete.py (Modified)
│   └── start_download() [+ All phases]
│
└── queue_status.py (New)
    ├── check_queue_status()
    └── notify_queue_update()
```

### Tasks
```
tasks/
└── cleanup_tasks.py (Extended)
    ├── cleanup_expired_cache()
    └── limit_cache_size()
```

---

## 🚀 Deployment Architecture

### Development
```
Laptop
├── Local Database (SQLite)
├── Temp Downloads
├── Bot Running
└── Logs
```

### Staging
```
Staging Server
├── PostgreSQL Database
├── Temp Downloads (50GB)
├── Bot Container
├── Monitoring
└── Logs
```

### Production
```
Production Cluster
├── PostgreSQL Database (Master+Replica)
├── Temp Downloads (100GB SSD)
├── Bot (2-3 instances)
├── Load Balancer
├── Monitoring & Alerts
├── Backup System
└── Logs (ELK Stack)
```

---

## 📈 Performance Metrics

### Before (Current)
```
Metric                  Value
─────────────────────────────────
Download (new)          2 min
Download (repeat)       2 min ❌
Parallel (3 files)      6 min ❌
Upload time             2 min
File size avg           100 MB ❌
Queue wait              30 min ❌
Throughput              0.5 files/min
Server CPU              40% avg
Server Memory           60% avg
```

### After (All Phases)
```
Metric                  Value
─────────────────────────────────
Download (new)          2 min
Download (repeat)       0.5s ✨ (99% faster)
Parallel (3 files)      2 min ✨ (67% faster)
Upload time             1 min ✨ (50% faster)
File size avg           60 MB ✨ (40% smaller)
Queue wait              10 min ✨ (67% less)
Throughput              1.5 files/min ✨ (3x better)
Server CPU              50% avg
Server Memory           50% avg
```

---

## 🔐 Security Considerations

### Cache Security
```
✅ Hash-based deduplication (SHA256)
✅ URL normalization to prevent duplicates
✅ Auto-expiry (30 days)
✅ Telegram file_id validation
```

### Resource Security
```
✅ Thread pool limiting (max 3)
✅ Memory monitoring
✅ CPU throttling
✅ Bandwidth limiting
```

### Data Security
```
✅ Database encryption
✅ Temporary file cleanup
✅ Access control logging
```

---

## 🎯 Success Metrics

### Technical
```
✅ Cache hit ratio: > 50%
✅ Response time: < 0.5s for cache
✅ Parallel efficiency: > 80%
✅ Compression ratio: 40%+ 
✅ Upload optimization: 50%+
✅ Test coverage: > 80%
✅ Error rate: < 1%
```

### Operational
```
✅ Uptime: 99.9%
✅ Deploy success: 100%
✅ Rollback time: < 5 min
✅ Alert response: < 5 min
```

### User
```
✅ User satisfaction: > 4.5/5
✅ Performance perception: +80%
✅ Feature adoption: > 70%
```

---

**نوشته شده:** 8 June 2026
**نسخه:** 1.0
