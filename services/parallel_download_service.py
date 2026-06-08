"""
PHASE 2: Parallel Download System
مدیریت دانلود‌های همزمان (تا 3 فایل موازی)
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional, List, Dict
from datetime import datetime
import yt_dlp
import os

logger = logging.getLogger(__name__)

# ============================================
# مرحله 2.1: ParallelDownloadManager
# ============================================

class ParallelDownloadManager:
    """
    مدیریت دانلود‌های همزمان با ThreadPoolExecutor
    
    Features:
    - دانلود تا 3 فایل موازی
    - Async interface
    - Progress tracking
    - Error handling
    - Resource monitoring
    """
    
    def __init__(self, max_workers: int = 3, download_dir: str = "temp_downloads"):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_downloads = {}  # {url: {status, progress, info}}
        self.lock = asyncio.Lock()
        self.max_workers = max_workers
        self.download_dir = download_dir
        self.ydl_opts = {
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
        }
        
        logger.info(f"[PARALLEL] ParallelDownloadManager initialized with {max_workers} workers")
    
    async def download_parallel(
        self,
        urls: List[str],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """
        دانلود چندین URL به صورت همزمان
        
        Args:
            urls: لیست URLs برای دانلود
            progress_callback: Async callback برای progress updates
        
        Returns:
            لیست نتایج [{'status': 'success/failed', 'file': path, 'error': msg}]
        """
        logger.info(f"[PARALLEL] Starting parallel download for {len(urls)} URLs")
        
        tasks = []
        for idx, url in enumerate(urls, 1):
            task = asyncio.create_task(
                self._download_single(url, progress_callback, idx, len(urls))
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"[PARALLEL] All downloads completed")
        return results
    
    async def _download_single(
        self,
        url: str,
        callback: Optional[Callable],
        current: int,
        total: int
    ) -> Dict:
        """
        دانلود یک فایل در background thread
        
        Args:
            url: URL برای دانلود
            callback: Progress callback
            current: شماره فایل جاری (برای نمایش)
            total: کل فایل‌ها
        
        Returns:
            {'status': 'success/failed', 'file': path, 'error': msg, 'info': info_dict}
        """
        loop = asyncio.get_event_loop()
        
        try:
            # ثبت در active downloads
            async with self.lock:
                self.active_downloads[url] = {
                    'status': 'downloading',
                    'progress': 0,
                    'start_time': datetime.utcnow(),
                    'current': current,
                    'total': total,
                    'speed': '0 MB/s',
                    'eta': '...',
                    'size': 0
                }
            
            logger.info(f"[PARALLEL #{current}] Starting download: {url[:60]}")
            
            # اجرای blocking download در executor
            result = await loop.run_in_executor(
                self.executor,
                self._blocking_download,
                url,
                callback
            )
            
            logger.info(f"[PARALLEL #{current}] ✅ Download completed")
            return result
            
        except Exception as e:
            logger.error(f"[PARALLEL #{current}] ❌ Download failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'file': None
            }
        finally:
            # پاک‌سازی از active downloads
            async with self.lock:
                if url in self.active_downloads:
                    del self.active_downloads[url]
    
    def _blocking_download(
        self,
        url: str,
        callback: Optional[Callable]
    ) -> Dict:
        """
        Blocking download برای ThreadPoolExecutor
        (اینجا blocking operations هستند)
        
        Args:
            url: URL برای دانلود
            callback: Progress callback (for future use)
        
        Returns:
            {'status': 'success', 'file': file_path, 'info': info_dict}
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                logger.info(f"[DOWNLOADER] Extracting info for: {url}")
                info = ydl.extract_info(url, download=True)
                
                file_path = ydl.prepare_filename(info)
                logger.info(f"[DOWNLOADER] File saved to: {file_path}")
                
                return {
                    'status': 'success',
                    'file': file_path,
                    'info': {
                        'title': info.get('title'),
                        'ext': info.get('ext'),
                        'size': info.get('filesize', 0),
                        'duration': info.get('duration', 0),
                        'url': url
                    }
                }
        except Exception as e:
            logger.error(f"[DOWNLOADER] Error: {e}")
            raise
    
    async def get_active_downloads(self) -> Dict:
        """بازگرداندن تمام دانلود‌های فعال"""
        async with self.lock:
            return dict(self.active_downloads)
    
    async def get_download_status(self, url: str) -> Optional[Dict]:
        """وضعیت یک دانلود مشخص"""
        async with self.lock:
            return self.active_downloads.get(url)
    
    async def cancel_download(self, url: str) -> bool:
        """لغو کردن یک دانلود (اگر ممکن باشد)"""
        async with self.lock:
            if url in self.active_downloads:
                self.active_downloads[url]['status'] = 'cancelled'
                logger.info(f"[PARALLEL] Download cancelled: {url}")
                return True
        return False
    
    def shutdown(self):
        """Shutdown executor"""
        self.executor.shutdown(wait=True)
        logger.info("[PARALLEL] ParallelDownloadManager shutdown")


# ============================================
# مرحله 2.2: DownloadCoordinator
# ============================================

class DownloadCoordinator:
    """
    مدیریت صف دانلود و هماهنگی‌سازی
    
    Features:
    - FIFO queue برای دانلود‌ها
    - محدود‌سازی دانلود‌های همزمان
    - User-specific queue tracking
    - Error recovery
    """
    
    def __init__(self, max_workers: int = 3):
        self.manager = ParallelDownloadManager(max_workers=max_workers)
        self.download_queue = asyncio.Queue()
        self.active_downloads = {}  # {user_id: [download_info]}
        self.user_queues = {}  # {user_id: queue_position}
        self.lock = asyncio.Lock()
        self.max_workers = max_workers
        
        logger.info("[COORDINATOR] DownloadCoordinator initialized")
    
    async def add_download(
        self,
        user_id: int,
        url: str,
        chat_id: int,
        priority: int = 1
    ) -> Dict:
        """
        افزودن دانلود به صف
        
        Args:
            user_id: ID کاربر
            url: URL برای دانلود
            chat_id: Chat ID برای ارسال نتیجه
            priority: اولویت (کمتر = بیشتر اولویت)
        
        Returns:
            {'position': int, 'eta_minutes': int, 'queue_length': int}
        """
        task = {
            'user_id': user_id,
            'url': url,
            'chat_id': chat_id,
            'priority': priority,
            'timestamp': datetime.utcnow(),
            'status': 'pending'
        }
        
        await self.download_queue.put(task)
        
        queue_size = self.download_queue.qsize()
        eta_minutes = (queue_size * 2)  # هر دانلود ~2 دقیقه
        
        logger.info(f"[COORDINATOR] Download added for user {user_id}, position: {queue_size}")
        
        return {
            'position': queue_size,
            'eta_minutes': eta_minutes,
            'queue_length': queue_size,
            'status': 'queued'
        }
    
    async def process_queue(self):
        """
        پردازش مستمر صف
        (این باید به صورت background task اجرا شود)
        """
        logger.info("[COORDINATOR] Starting queue processor")
        
        while True:
            try:
                # بررسی اینکه آیا محل برای دانلود بعدی است
                current_active = len(self.active_downloads)
                
                if current_active < self.max_workers:
                    try:
                        # گرفتن task از صف (با timeout)
                        task = await asyncio.wait_for(
                            self.download_queue.get(),
                            timeout=1.0
                        )
                        
                        # اجرای دانلود
                        await self.execute_download(task)
                        
                    except asyncio.TimeoutError:
                        # صف خالی است، منتظر بمان
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        logger.error(f"[COORDINATOR] Queue processing error: {e}")
                else:
                    # تمام workers مشغول هستند
                    await asyncio.sleep(1)
            
            except Exception as e:
                logger.error(f"[COORDINATOR] Critical error: {e}")
                await asyncio.sleep(5)
    
    async def execute_download(self, task: Dict) -> None:
        """
        اجرای یک دانلود
        
        Args:
            task: Task dict with user_id, url, chat_id, etc
        """
        user_id = task['user_id']
        url = task['url']
        
        try:
            # ثبت در active downloads
            async with self.lock:
                if user_id not in self.active_downloads:
                    self.active_downloads[user_id] = []
                
                self.active_downloads[user_id].append({
                    'url': url,
                    'status': 'downloading',
                    'started_at': datetime.utcnow()
                })
            
            logger.info(f"[COORDINATOR] Executing download for user {user_id}: {url[:60]}")
            
            # اجرای دانلود
            result = await self.manager.download_parallel([url])
            
            if result and result[0]['status'] == 'success':
                logger.info(f"[COORDINATOR] Download successful for user {user_id}")
                await self._handle_download_complete(user_id, task, result[0])
            else:
                logger.error(f"[COORDINATOR] Download failed for user {user_id}")
                await self._handle_download_error(user_id, task, result[0].get('error'))
        
        except Exception as e:
            logger.error(f"[COORDINATOR] Error executing download: {e}")
            await self._handle_download_error(user_id, task, str(e))
        
        finally:
            # پاک‌سازی
            async with self.lock:
                if user_id in self.active_downloads:
                    self.active_downloads[user_id] = [
                        d for d in self.active_downloads[user_id]
                        if d['url'] != url
                    ]
                    if not self.active_downloads[user_id]:
                        del self.active_downloads[user_id]
    
    async def _handle_download_complete(
        self,
        user_id: int,
        task: Dict,
        result: Dict
    ) -> None:
        """مدیریت دانلود موفق"""
        logger.info(f"[COORDINATOR] Download complete for user {user_id}")
        # اینجا می‌توانید callback اضافه کنید برای ارسال پیام
    
    async def _handle_download_error(
        self,
        user_id: int,
        task: Dict,
        error: str
    ) -> None:
        """مدیریت خطای دانلود"""
        logger.error(f"[COORDINATOR] Download error for user {user_id}: {error}")
        # اینجا می‌توانید callback اضافه کنید برای اطلاع‌رسانی کاربر
    
    async def get_queue_position(self, user_id: int, url: str) -> int:
        """
        گرفتن موقعیت دانلود در صف
        
        Args:
            user_id: ID کاربر
            url: URL دانلود
        
        Returns:
            موقعیت در صف (1-based)
        """
        queue_items = []
        temp_queue = asyncio.Queue()
        
        # خالی کردن صف موقت برای سازمان‌دهی
        while not self.download_queue.empty():
            try:
                item = self.download_queue.get_nowait()
                queue_items.append(item)
            except asyncio.QueueEmpty:
                break
        
        # دوباره پر کردن صف
        for item in queue_items:
            await self.download_queue.put(item)
        
        # یافتن موقعیت
        for idx, item in enumerate(queue_items, 1):
            if item['user_id'] == user_id and item['url'] == url:
                return idx
        
        return -1  # نیافت
    
    async def get_queue_stats(self) -> Dict:
        """آمار صف"""
        return {
            'queue_length': self.download_queue.qsize(),
            'active_downloads': len(self.active_downloads),
            'max_concurrent': self.max_workers,
            'available_slots': max(0, self.max_workers - len(self.active_downloads))
        }
    
    async def get_user_downloads(self, user_id: int) -> List[Dict]:
        """تمام دانلود‌های کاربر"""
        async with self.lock:
            return self.active_downloads.get(user_id, [])
    
    def shutdown(self):
        """Shutdown coordinator"""
        self.manager.shutdown()
        logger.info("[COORDINATOR] DownloadCoordinator shutdown")


# ============================================
# Global Coordinator Instance
# ============================================

_global_coordinator: Optional[DownloadCoordinator] = None


async def get_coordinator() -> DownloadCoordinator:
    """گرفتن global coordinator instance"""
    global _global_coordinator
    if _global_coordinator is None:
        _global_coordinator = DownloadCoordinator(max_workers=3)
    return _global_coordinator


__all__ = [
    'ParallelDownloadManager',
    'DownloadCoordinator',
    'get_coordinator'
]
