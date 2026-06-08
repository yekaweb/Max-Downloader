# 🏗️ PHASES 2-5: SKELETON & IMPLEMENTATION GUIDE

## مقدمه

این فایل شامل skeleton code و راهنمای مفصل برای Phases 2-5 است.
هر phase بصورت مستقل قابل پیاده‌سازی است.

---

# 🟡 PHASE 2: Parallel Download System

## 2.1: ParallelDownloadManager

**فایل:** `/services/parallel_download_service.py`

```python
"""PHASE 2: Parallel Download Manager"""
from concurrent.futures import ThreadPoolExecutor
import asyncio
from typing import List, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class ParallelDownloadManager:
    """
    Manage concurrent downloads (max 3 at a time)
    
    Features:
    - ThreadPoolExecutor for CPU-bound operations
    - Async interface for handlers
    - Progress tracking
    - Error handling
    - Resource monitoring
    """
    
    def __init__(self, max_workers: int = 3):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_downloads = {}
        self.lock = asyncio.Lock()
    
    async def download_parallel(
        self,
        urls: List[str],
        progress_callback: Optional[Callable] = None
    ) -> List[dict]:
        """Download multiple URLs in parallel"""
        # Implementation here
        pass
    
    async def _download_single(
        self,
        url: str,
        callback: Optional[Callable]
    ):
        """Download single URL"""
        # Implementation here
        pass

# Configuration:
# MAX_WORKERS = 3        # 3 concurrent downloads
# CPU_LIMIT = 80%        # Stop if CPU > 80%
# MEMORY_LIMIT = 500MB   # Max per download
```

---

## 2.2: Download Coordinator

**فایل:** `/services/parallel_download_service.py` (Part 2)

```python
class DownloadCoordinator:
    """Coordinate queue and parallel downloads"""
    
    def __init__(self, max_workers: int = 3):
        self.manager = ParallelDownloadManager(max_workers)
        self.download_queue = asyncio.Queue()
        self.active_downloads = {}
    
    async def process_queue(self):
        """Process download queue"""
        # Implementation here
        pass
    
    async def add_download(self, user_id: int, url: str, priority: int = 1):
        """Add download to queue"""
        # Implementation here
        pass

# Usage:
# coordinator = DownloadCoordinator()
# await coordinator.add_download(user_id=123, url="https://...")
```

---

## 2.3: Progress Tracking

**متعلق به:** `/services/parallel_download_service.py`

```python
async def generate_parallel_progress(downloads: dict) -> str:
    """Generate progress message for multiple downloads"""
    message = "📥 **Downloads in Progress:**\n\n"
    
    for idx, (url, info) in enumerate(downloads.items(), 1):
        progress_pct = info.get('progress', 0)
        progress_bar = "█" * int(progress_pct/5) + "░" * (20 - int(progress_pct/5))
        message += f"#{idx} {progress_bar} {progress_pct:.0f}%\n"
    
    return message
```

---

# 🟢 PHASE 3: Stream Upload System

## 3.1: StreamUploadService

**فایل:** `/services/stream_upload_service.py`

```python
"""PHASE 3: Stream Upload Service"""
import aiofiles
import asyncio
from pathlib import Path
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)

class StreamUploadService:
    """
    Upload files in chunks while downloading
    
    Benefits:
    - 50% faster uploads
    - Less memory usage
    - Parallel D/U
    - Better for large files
    """
    
    def __init__(self, chunk_size: int = 5 * 1024 * 1024):  # 5MB
        self.chunk_size = chunk_size
        self.upload_queue = asyncio.Queue()
    
    async def stream_upload_to_telegram(
        self,
        file_path: str,
        chat_id: int,
        bot,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """Upload file in chunks"""
        # Implementation here
        pass
    
    async def _upload_chunks(self, chunks: list, chat_id: int, bot):
        """Upload chunk batch"""
        # Implementation here
        pass

# Configuration:
# CHUNK_SIZE = 5MB       # Size of each chunk
# MAX_CHUNKS = 3         # Max parallel uploads
```

---

## 3.2: Buffer Management

**متعلق به:** `/services/stream_upload_service.py`

```python
class BufferManager:
    """Manage buffer for streaming uploads"""
    
    def __init__(self, max_buffer_size: int = 50 * 1024 * 1024):  # 50MB
        self.max_buffer = max_buffer_size
        self.current_buffer = 0
        self.lock = asyncio.Lock()
    
    async def can_add_chunk(self, chunk_size: int) -> bool:
        """Check if buffer has space"""
        async with self.lock:
            if self.current_buffer + chunk_size <= self.max_buffer:
                self.current_buffer += chunk_size
                return True
            return False
    
    async def release_buffer(self, chunk_size: int):
        """Free up buffer space after upload"""
        # Implementation here
        pass
```

---

# 🟠 PHASE 4: Compression System

## 4.1: CompressionService

**فایل:** `/services/compression_service.py`

```python
"""PHASE 4: Compression Service using FFmpeg"""
import subprocess
import asyncio
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)

class CompressionService:
    """
    Compress videos/audio using FFmpeg
    
    Goals:
    - 40% file size reduction
    - Quality preservation
    - Fast compression (< 1 min per file)
    """
    
    VIDEO_PRESETS = {
        'fast': {
            'codec': 'libx264',
            'crf': 23,      # 0-51, lower = better quality
            'preset': 'fast'
        },
        'balanced': {
            'codec': 'libx264',
            'crf': 25,
            'preset': 'medium'
        }
    }
    
    @staticmethod
    async def compress_video(
        input_file: str,
        output_file: str,
        preset: str = 'fast',
        progress_callback: Optional[Callable] = None
    ) -> dict:
        """Compress video"""
        # Implementation here
        pass
    
    @staticmethod
    async def compress_audio(
        input_file: str,
        output_file: str,
        bitrate: str = '128k'
    ) -> dict:
        """Compress audio"""
        # Implementation here
        pass

# Configuration:
# PRESETS: fast, balanced, high-quality
# CRF: 23 default (quality)
# FORMATS: H.264, VP9, AV1
```

---

## 4.2: Adaptive Compression

**متعلق به:** `/services/compression_service.py`

```python
class AdaptiveCompression:
    """Different compression for different platforms"""
    
    PLATFORM_PRESETS = {
        'youtube': {
            'codec': 'h264_balanced',
            'max_resolution': '1920x1080',
            'target_bitrate': '5000k'
        },
        'instagram': {
            'codec': 'h264_fast',
            'max_resolution': '1080x1080',
            'target_bitrate': '2500k'
        },
        'telegram': {
            'codec': 'h264_fast',
            'max_resolution': '1280x720',
            'target_bitrate': '1000k'
        }
    }
    
    @staticmethod
    async def auto_compress(
        input_file: str,
        platform: str,
        max_file_size_mb: int = 50
    ) -> str:
        """Automatically compress based on platform"""
        # Implementation here
        pass
```

---

# 🔴 PHASE 5: Queue Management System

## 5.1: PriorityQueueManager

**فایل:** `/services/queue_service.py`

```python
"""PHASE 5: Priority Queue Management"""
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import heapq
import asyncio
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class Priority(Enum):
    CRITICAL = 0  # Admin
    HIGH = 1      # Premium users
    NORMAL = 2    # Regular users
    LOW = 3       # Free users

@dataclass
class DownloadTask:
    """Represents a download in the queue"""
    priority: Priority
    timestamp: float
    user_id: int
    url: str
    chat_id: int
    
    def __lt__(self, other):
        """For heap sorting"""
        if self.priority.value == other.priority.value:
            return self.timestamp < other.timestamp
        return self.priority.value < other.priority.value

class PriorityQueueManager:
    """
    Manage downloads with priority
    
    Features:
    - Priority-based scheduling
    - Fair distribution
    - Position tracking
    - ETA calculation
    """
    
    def __init__(self, max_concurrent: int = 3):
        self.queue = []
        self.active_tasks = {}
        self.max_concurrent = max_concurrent
        self.lock = asyncio.Lock()
    
    async def add_task(self, task: DownloadTask) -> int:
        """Add task to queue, return position"""
        # Implementation here
        pass
    
    async def get_next_task(self) -> Optional[DownloadTask]:
        """Get next task for processing"""
        # Implementation here
        pass
    
    async def get_queue_position(self, user_id: int, url: str) -> int:
        """Get user's position in queue"""
        # Implementation here
        pass

# Configuration:
# MAX_CONCURRENT = 3     # 3 active downloads
# PRIORITY_LEVELS = 4    # Critical, High, Normal, Low
```

---

## 5.2: Resource Monitoring

**متعلق به:** `/services/queue_service.py`

```python
class ResourceManager:
    """Monitor system resources"""
    
    def __init__(self):
        self.cpu_usage = 0
        self.memory_usage = 0
    
    async def monitor_resources(self):
        """Continuous monitoring"""
        # Using psutil
        # Adjust max_workers based on resources
        pass
    
    def get_resource_status(self) -> dict:
        """Return current resource status"""
        return {
            'cpu_percent': self.cpu_usage,
            'memory_percent': self.memory_usage,
            'status': 'healthy' if self.cpu_usage < 70 else 'stressed'
        }

# Triggers:
# CPU > 80%: Reduce workers
# Memory > 85%: Pause new tasks
# Bandwidth < 100KB/s: Slow network warning
```

---

## 5.3: User Notifications

**متعلق به:** `/services/queue_service.py`

```python
class QueueNotificationService:
    """Notify users about queue status"""
    
    @staticmethod
    async def notify_queue_position(
        bot,
        chat_id: int,
        position: int,
        eta_minutes: int
    ):
        """Send queue position to user"""
        message = f"""
📋 **Queue Position: #{position}**

⏱️ ETA: {eta_minutes} minutes
🔄 Active Downloads: 3/3
👥 Behind you: {position - 1}

💡 Tip: Premium users skip the queue!
"""
        await bot.send_message(chat_id, message)

# Message Templates:
# - Queued notification
# - Position update
# - Download starting
# - Completion notification
```

---

# 🚀 Implementation Roadmap

## Phase 2: Week 1-2
```
Mon: Parallel manager architecture
Tue: Download coordinator
Wed: Progress tracking
Thu: Handler integration
Fri: Testing & deployment
```

## Phase 3: Week 2-3
```
Mon: Stream upload service
Tue: Buffer management
Wed: Parallel D/U integration
Thu: Performance testing
Fri: Deployment
```

## Phase 4: Week 3-4
```
Mon: FFmpeg wrapper
Tue: Adaptive compression
Wed: Handler integration
Thu: Quality testing
Fri: Deployment
```

## Phase 5: Week 4-5
```
Mon: Priority queue
Tue: Resource monitoring
Wed: User notifications
Thu: Integration testing
Fri: Deployment
```

---

# 📊 Architecture Diagram

```
┌──────────────────────────────────────┐
│    Telegram Bot (v2.0 Enhanced)      │
├──────────────────────────────────────┤
│                                      │
│ Phase 1: Cache ✅                   │
│   ├─ Check URL in database          │
│   └─ Send cached file (0.5s)        │
│                                      │
│ Phase 2: Parallel (Planning)        │
│   ├─ Download 3 files at once       │
│   └─ ThreadPoolExecutor             │
│                                      │
│ Phase 3: Stream (Planning)          │
│   ├─ Upload chunks in parallel      │
│   └─ 50% faster                     │
│                                      │
│ Phase 4: Compression (Planning)     │
│   ├─ FFmpeg compression             │
│   └─ 40% smaller                    │
│                                      │
│ Phase 5: Queue (Planning)           │
│   ├─ Priority-based                 │
│   └─ 60% less wait                  │
│                                      │
└──────────────────────────────────────┘
```

---

# 📝 Usage Example (Future)

```python
# After all phases are complete:

# User sends URL
url = "https://youtube.com/watch?v=xyz"

# Phase 1: Check cache
cached = await cache_service.get_cached_file_id(url, session)
if cached:
    await message.reply_document(cached)  # 0.5 second! ✨
    return

# Phase 2: Add to parallel queue
await coordinator.add_download(user_id, url)

# Wait for processing...

# Phase 2: Download in parallel (3 concurrent)
# Phase 4: Compress (40% smaller)
# Phase 3: Upload in chunks (50% faster)

# Phase 1: Save to cache for next time
await cache_service.save_to_cache(url, file_id, info, session)

# Phase 5: Update stats and queue
```

---

# 🎯 Success Metrics (All Phases)

```
Performance:
├─ Phase 1: 0.5s cache hit ✅
├─ Phase 2: 3 concurrent downloads ⏳
├─ Phase 3: 50% faster upload ⏳
├─ Phase 4: 40% file reduction ⏳
└─ Phase 5: 60% less wait time ⏳

Quality:
├─ Code coverage: >80%
├─ Tests passing: 100%
├─ Error rate: <1%
└─ Uptime: 99.9%

User Experience:
├─ Performance improvement: +80%
├─ User satisfaction: >4.5/5
└─ Feature adoption: >70%
```

---

**Status:** Phase 1 ✅ Complete | Phases 2-5 📋 Planned
**Next:** Start Phase 2 when Phase 1 tests pass
**Estimated Total Time:** 30-40 hours of development
