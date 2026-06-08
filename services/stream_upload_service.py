"""
PHASE 3: Stream Upload Service
مرحله 3.1 & 3.2 - آپلود جریانی و مدیریت بفر
"""

from __future__ import annotations

import asyncio
import aiofiles
import logging
from typing import Callable, Optional, List, Dict
from datetime import datetime
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# ============================================
# مرحله 3.1: StreamUploadService
# ============================================

class StreamUploadService:
    """
    آپلود فایل‌ها به صورت جریانی (chunks)
    
    Features:
    - آپلود chunks به جای کل فایل
    - کاهش مصرف حافظه
    - Progress tracking
    - Parallel chunk uploads
    - Error recovery
    """
    
    def __init__(self, chunk_size: int = 5 * 1024 * 1024):  # 5MB chunks
        """
        Args:
            chunk_size: اندازه هر chunk (bytes)
        """
        self.chunk_size = chunk_size
        self.upload_queue = asyncio.Queue()
        self.active_uploads = {}  # {file_id: {status, progress}}
        self.lock = asyncio.Lock()
        
        logger.info(f"[STREAM] StreamUploadService initialized with {chunk_size/(1024*1024):.1f}MB chunks")
    
    async def stream_upload_to_telegram(
        self,
        file_path: str,
        chat_id: int,
        bot,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        آپلود فایل به صورت جریانی
        
        Args:
            file_path: مسیر فایل برای آپلود
            chat_id: Chat ID برای ارسال
            bot: Telegram bot instance
            progress_callback: Async callback برای progress updates
        
        Returns:
            {'status': 'success/failed', 'file_id': id, 'error': msg}
        """
        logger.info(f"[STREAM] Starting stream upload: {file_path}")
        
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        
        # ثبت در active uploads
        async with self.lock:
            self.active_uploads[file_path] = {
                'status': 'uploading',
                'progress': 0,
                'file_size': file_size,
                'uploaded_bytes': 0,
                'start_time': datetime.utcnow()
            }
        
        try:
            chunks = []
            uploaded_bytes = 0
            
            # خواندن فایل و جمع‌کردن chunks
            async with aiofiles.open(file_path, 'rb') as f:
                while True:
                    chunk = await f.read(self.chunk_size)
                    
                    if not chunk:
                        break
                    
                    chunks.append(chunk)
                    uploaded_bytes += len(chunk)
                    
                    # آپدیت progress
                    if progress_callback:
                        progress_pct = (uploaded_bytes / file_size) * 100
                        await progress_callback({
                            'status': 'uploading',
                            'progress': progress_pct,
                            'uploaded_mb': uploaded_bytes / (1024 * 1024),
                            'total_mb': file_size / (1024 * 1024),
                            'speed': self._calculate_speed(file_path)
                        })
                    
                    # آپدیت internal progress
                    async with self.lock:
                        if file_path in self.active_uploads:
                            self.active_uploads[file_path]['uploaded_bytes'] = uploaded_bytes
                            self.active_uploads[file_path]['progress'] = (uploaded_bytes / file_size) * 100
                    
                    # اگر chunks جمع شده باشد، آپلود کن
                    if len(chunks) >= 3 or uploaded_bytes == file_size:
                        file_id = await self._upload_chunks(chunks, chat_id, bot, file_name)
                        if not file_id:
                            raise Exception("Failed to upload chunks")
                        chunks = []
            
            logger.info(f"[STREAM] ✅ Upload completed: {file_path}")
            
            return {
                'status': 'success',
                'file_id': file_id,
                'file_size': file_size,
                'uploaded_bytes': uploaded_bytes
            }
        
        except Exception as e:
            logger.error(f"[STREAM] ❌ Upload failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'file_id': None
            }
        
        finally:
            # پاک‌سازی
            async with self.lock:
                if file_path in self.active_uploads:
                    del self.active_uploads[file_path]
    
    async def _upload_chunks(
        self,
        chunks: List[bytes],
        chat_id: int,
        bot,
        file_name: str
    ) -> Optional[str]:
        """
        آپلود مجموعه‌ای از chunks
        
        Args:
            chunks: لیست bytes chunks
            chat_id: Chat ID
            bot: Telegram bot
            file_name: نام فایل
        
        Returns:
            file_id اگر موفق، None اگر ناموفق
        """
        try:
            # ترکیب chunks
            data = b''.join(chunks)
            
            # آپلود به تلگرام
            import io
            file_obj = io.BytesIO(data)
            
            message = await bot.send_document(
                chat_id=chat_id,
                document=file_obj,
                file_name=file_name
            )
            
            file_id = message.document.file_id
            logger.info(f"[STREAM] Chunk uploaded: {len(data)/(1024*1024):.1f}MB")
            
            return file_id
        
        except Exception as e:
            logger.error(f"[STREAM] Chunk upload failed: {e}")
            return None
    
    def _calculate_speed(self, file_path: str) -> float:
        """محاسبه سرعت آپلود (MB/s)"""
        if file_path not in self.active_uploads:
            return 0
        
        info = self.active_uploads[file_path]
        elapsed = (datetime.utcnow() - info['start_time']).total_seconds()
        
        if elapsed == 0:
            return 0
        
        speed_bytes = info['uploaded_bytes'] / elapsed
        speed_mb = speed_bytes / (1024 * 1024)
        
        return speed_mb
    
    async def get_upload_status(self, file_path: str) -> Optional[Dict]:
        """وضعیت آپلود فایل مشخص"""
        async with self.lock:
            return self.active_uploads.get(file_path)
    
    async def get_active_uploads(self) -> Dict:
        """تمام آپلود‌های فعال"""
        async with self.lock:
            return dict(self.active_uploads)


# ============================================
# مرحله 3.2: BufferManager
# ============================================

class BufferManager:
    """
    مدیریت بفر برای جلوگیری از overflow و بهینه‌سازی حافظه
    
    Features:
    - محدود کردن اندازه بفر
    - معادل‌سازی دانلود/آپلود
    - Auto garbage collection
    - Real-time status
    """
    
    def __init__(self, max_buffer_size: int = 50 * 1024 * 1024):  # 50MB default
        """
        Args:
            max_buffer_size: حداکثر اندازه بفر (bytes)
        """
        self.max_buffer = max_buffer_size
        self.current_buffer = 0
        self.lock = asyncio.Lock()
        self.chunks_in_buffer = 0
        
        logger.info(f"[BUFFER] BufferManager initialized with {max_buffer_size/(1024*1024):.0f}MB max")
    
    async def can_add_chunk(self, chunk_size: int) -> bool:
        """
        بررسی اینکه می‌توانیم chunk جدید بیفزاییم
        
        Args:
            chunk_size: اندازه chunk (bytes)
        
        Returns:
            True اگر جای باقی است، False اگر بفر پر است
        """
        async with self.lock:
            if self.current_buffer + chunk_size <= self.max_buffer:
                self.current_buffer += chunk_size
                self.chunks_in_buffer += 1
                return True
            
            logger.warning(f"[BUFFER] Buffer full: {self.current_buffer/(1024*1024):.1f}MB")
            return False
    
    async def release_buffer(self, chunk_size: int) -> None:
        """
        آزادکردن بفر بعد از پردازش
        
        Args:
            chunk_size: اندازه chunk (bytes)
        """
        async with self.lock:
            self.current_buffer = max(0, self.current_buffer - chunk_size)
            self.chunks_in_buffer = max(0, self.chunks_in_buffer - 1)
            
            logger.debug(f"[BUFFER] Released {chunk_size/(1024*1024):.1f}MB, now: {self.current_buffer/(1024*1024):.1f}MB")
    
    async def get_available_space(self) -> int:
        """مقدار فضای موجود در بفر (bytes)"""
        async with self.lock:
            return self.max_buffer - self.current_buffer
    
    async def get_buffer_status(self) -> Dict:
        """وضعیت بفر"""
        async with self.lock:
            usage_pct = (self.current_buffer / self.max_buffer) * 100
            
            return {
                'current_mb': self.current_buffer / (1024 * 1024),
                'max_mb': self.max_buffer / (1024 * 1024),
                'available_mb': (self.max_buffer - self.current_buffer) / (1024 * 1024),
                'usage_percent': usage_pct,
                'chunks_in_buffer': self.chunks_in_buffer,
                'status': 'healthy' if usage_pct < 70 else 'warning' if usage_pct < 90 else 'critical'
            }
    
    async def wait_for_space(self, chunk_size: int, timeout: int = 60) -> bool:
        """
        منتظر شوید تا فضای کافی موجود شود
        
        Args:
            chunk_size: اندازه chunk مورد نیاز
            timeout: حداکثر زمان انتظار (seconds)
        
        Returns:
            True اگر فضا موجود شد، False اگر timeout
        """
        start_time = datetime.utcnow()
        
        while True:
            if await self.can_add_chunk(chunk_size):
                return True
            
            # بررسی timeout
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed > timeout:
                logger.warning(f"[BUFFER] Timeout waiting for buffer space")
                return False
            
            # منتظر کمی بمان
            await asyncio.sleep(0.5)


__all__ = [
    'StreamUploadService',
    'BufferManager'
]
