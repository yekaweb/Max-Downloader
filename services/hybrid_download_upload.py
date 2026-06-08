"""
PHASE 3: Hybrid Download/Upload Service
مرحله 3.3 - ادغام دانلود و آپلود موازی
"""

import asyncio
import logging
from typing import Callable, Optional, Dict
from datetime import datetime
from services.parallel_download_service import ParallelDownloadManager
from services.stream_upload_service import StreamUploadService, BufferManager

logger = logging.getLogger(__name__)

# ============================================
# مرحله 3.3: HybridDownloadUpload
# ============================================

class HybridDownloadUpload:
    """
    دانلود و آپلود موازی (جریانی)
    
    Features:
    - دانلود chunks و قرار دادن در بفر
    - آپلود chunks از بفر
    - Buffer management
    - Progress tracking (دانلود + آپلود)
    - Auto synchronization
    """
    
    def __init__(
        self,
        max_concurrent_downloads: int = 3,
        max_buffer_mb: int = 50
    ):
        """
        Args:
            max_concurrent_downloads: حداکثر دانلود‌های موازی
            max_buffer_mb: حداکثر اندازه بفر (MB)
        """
        self.download_manager = ParallelDownloadManager(max_workers=max_concurrent_downloads)
        self.upload_service = StreamUploadService()
        self.buffer_manager = BufferManager(max_buffer_size=max_buffer_mb * 1024 * 1024)
        
        self.download_buffer = asyncio.Queue()
        self.upload_buffer = asyncio.Queue()
        
        self.active_hybrid_tasks = {}  # {file_path: {status, progress_d, progress_u}}
        self.lock = asyncio.Lock()
        
        logger.info(
            f"[HYBRID] HybridDownloadUpload initialized\n"
            f"         Downloads: {max_concurrent_downloads}, Buffer: {max_buffer_mb}MB"
        )
    
    async def download_compress_upload_parallel(
        self,
        url: str,
        chat_id: int,
        bot,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        دانلود، کمپرس و آپلود یک فایل به صورت جریانی
        
        Args:
            url: URL برای دانلود
            chat_id: Chat ID برای ارسال
            bot: Telegram bot instance
            progress_callback: Async callback برای progress
        
        Returns:
            {'status': 'success/failed', 'duration': time, 'total_size': bytes}
        """
        logger.info(f"[HYBRID] Starting hybrid D/U for: {url[:60]}")
        
        start_time = datetime.utcnow()
        
        try:
            # ثبت در active tasks
            async with self.lock:
                self.active_hybrid_tasks[url] = {
                    'status': 'downloading',
                    'progress_download': 0,
                    'progress_upload': 0,
                    'start_time': start_time
                }
            
            # Task برای دانلود
            download_task = asyncio.create_task(
                self._download_with_buffer(url, progress_callback)
            )
            
            # Task برای آپلود
            upload_task = asyncio.create_task(
                self._upload_from_buffer(chat_id, bot, progress_callback)
            )
            
            # منتظر هر دو task
            results = await asyncio.gather(
                download_task,
                upload_task,
                return_exceptions=True
            )
            
            # بررسی خطاها
            if isinstance(results[0], Exception):
                raise results[0]
            if isinstance(results[1], Exception):
                raise results[1]
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"[HYBRID] ✅ Completed in {duration:.1f}s")
            
            return {
                'status': 'success',
                'duration': duration,
                'download_result': results[0],
                'upload_result': results[1]
            }
        
        except Exception as e:
            logger.error(f"[HYBRID] ❌ Error: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'duration': (datetime.utcnow() - start_time).total_seconds()
            }
        
        finally:
            # پاک‌سازی
            async with self.lock:
                if url in self.active_hybrid_tasks:
                    del self.active_hybrid_tasks[url]
    
    async def _download_with_buffer(
        self,
        url: str,
        progress_callback: Optional[Callable]
    ) -> Dict:
        """
        دانلود و قرار دادن chunks در بفر
        
        Args:
            url: URL برای دانلود
            progress_callback: Progress callback
        
        Returns:
            Download result dict
        """
        logger.info(f"[HYBRID-D] Download task started")
        
        try:
            # دانلود فایل
            results = await self.download_manager.download_parallel(
                [url],
                progress_callback=progress_callback
            )
            
            if results[0]['status'] != 'success':
                raise Exception(f"Download failed: {results[0].get('error')}")
            
            file_path = results[0]['file']
            
            # قرار دادن signal شروع در بفر
            await self.download_buffer.put({
                'type': 'start',
                'file_path': file_path
            })
            
            logger.info(f"[HYBRID-D] ✅ Download completed: {file_path}")
            
            # قرار دادن signal پایان در بفر
            await self.download_buffer.put({
                'type': 'end'
            })
            
            return results[0]
        
        except Exception as e:
            logger.error(f"[HYBRID-D] Error: {e}")
            await self.download_buffer.put({'type': 'error', 'error': str(e)})
            raise
    
    async def _upload_from_buffer(
        self,
        chat_id: int,
        bot,
        progress_callback: Optional[Callable]
    ) -> Dict:
        """
        خواندن از بفر و آپلود
        
        Args:
            chat_id: Chat ID
            bot: Telegram bot
            progress_callback: Progress callback
        
        Returns:
            Upload result dict
        """
        logger.info(f"[HYBRID-U] Upload task started")
        
        try:
            file_path = None
            
            while True:
                # دریافت از بفر
                item = await self.download_buffer.get()
                
                if item['type'] == 'start':
                    file_path = item['file_path']
                    logger.info(f"[HYBRID-U] Upload starting for: {file_path}")
                
                elif item['type'] == 'end':
                    logger.info(f"[HYBRID-U] ✅ Upload completed")
                    break
                
                elif item['type'] == 'error':
                    raise Exception(item['error'])
            
            if file_path:
                # آپلود فایل
                result = await self.upload_service.stream_upload_to_telegram(
                    file_path,
                    chat_id,
                    bot,
                    progress_callback
                )
                
                return result
            
            return {'status': 'success'}
        
        except Exception as e:
            logger.error(f"[HYBRID-U] Error: {e}")
            raise
    
    async def get_hybrid_status(self, url: str) -> Optional[Dict]:
        """وضعیت دانلود/آپلود"""
        async with self.lock:
            return self.active_hybrid_tasks.get(url)
    
    async def get_buffer_status(self) -> Dict:
        """وضعیت بفر"""
        return await self.buffer_manager.get_buffer_status()
    
    async def get_all_hybrid_tasks(self) -> Dict:
        """تمام hybrid tasks فعال"""
        async with self.lock:
            return dict(self.active_hybrid_tasks)


# ============================================
# Global Hybrid Instance
# ============================================

_global_hybrid: Optional[HybridDownloadUpload] = None


async def get_hybrid_service() -> HybridDownloadUpload:
    """گرفتن global hybrid instance"""
    global _global_hybrid
    if _global_hybrid is None:
        _global_hybrid = HybridDownloadUpload(
            max_concurrent_downloads=3,
            max_buffer_mb=50
        )
    return _global_hybrid


__all__ = [
    'HybridDownloadUpload',
    'get_hybrid_service'
]
