"""
PHASE 2: Progress Tracking System
مرحله 2.3 - نمایش پیشرفت دانلود‌های متعدد
"""

import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ProgressTracker:
    """
    ردیابی و نمایش پیشرفت دانلود‌های متعدد
    """
    
    @staticmethod
    def format_bytes(bytes_size: int) -> str:
        """تبدیل bytes به KB/MB/GB"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f}TB"
    
    @staticmethod
    def format_time(seconds: int) -> str:
        """تبدیل seconds به HH:MM:SS"""
        if seconds < 0:
            return "N/A"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        elif minutes > 0:
            return f"{minutes}:{secs:02d}m"
        else:
            return f"{secs}s"
    
    @staticmethod
    def format_speed(bytes_per_sec: float) -> str:
        """تبدیل bytes/sec به MB/s"""
        if bytes_per_sec == 0:
            return "0 MB/s"
        mb_per_sec = bytes_per_sec / (1024 * 1024)
        return f"{mb_per_sec:.1f} MB/s"
    
    @staticmethod
    def generate_progress_bar(
        current: int,
        total: int,
        width: int = 20
    ) -> str:
        """
        تولید نوار پیشرفت
        
        Args:
            current: مقدار فعلی
            total: کل مقدار
            width: عرض نوار
        
        Returns:
            نوار پیشرفت (مثال: █████░░░░░░░░░░░░░░)
        """
        if total == 0:
            return "░" * width
        
        filled = int((current / total) * width)
        filled = min(filled, width)
        
        bar = "█" * filled + "░" * (width - filled)
        return bar
    
    @staticmethod
    async def generate_single_progress(
        download_info: Dict,
        index: int,
        total_downloads: int
    ) -> str:
        """
        تولید پیام پیشرفت برای یک دانلود
        
        Args:
            download_info: اطلاعات دانلود
            index: شماره دانلود (1-based)
            total_downloads: کل دانلود‌ها
        
        Returns:
            پیام پیشرفت فرمت‌شده
        """
        url = download_info.get('url', 'Unknown')[:50]
        progress = download_info.get('progress', 0)
        speed = download_info.get('speed', 0)
        eta = download_info.get('eta', 0)
        size = download_info.get('size', 0)
        
        progress_bar = ProgressTracker.generate_progress_bar(int(progress), 100)
        speed_str = ProgressTracker.format_speed(speed)
        eta_str = ProgressTracker.format_time(eta)
        size_str = ProgressTracker.format_bytes(size)
        
        message = (
            f"*#{index}/{total_downloads}*\n"
            f"{progress_bar} {progress:.0f}%\n"
            f"🔗 {url}...\n"
            f"⚡ {speed_str}\n"
            f"⏱️ ETA: {eta_str}\n"
            f"📦 Size: {size_str}\n"
        )
        
        return message
    
    @staticmethod
    async def generate_parallel_progress(
        downloads: Dict[str, Dict],
        title: str = "📥 **دانلود‌های جاری**"
    ) -> str:
        """
        تولید پیام پیشرفت برای دانلود‌های متعدد
        
        Args:
            downloads: dict of {url: {status, progress, speed, eta, size}}
            title: عنوان پیام
        
        Returns:
            پیام پیشرفت کامل فرمت‌شده
        """
        if not downloads:
            return f"{title}\n\nبدون دانلود فعال"
        
        message = f"{title}\n\n"
        
        total_progress = 0
        total_size = 0
        active_count = 0
        
        for idx, (url, info) in enumerate(downloads.items(), 1):
            status = info.get('status', 'unknown')
            
            if status != 'downloading':
                continue
            
            active_count += 1
            
            progress = info.get('progress', 0)
            speed = info.get('speed', 0)
            eta = info.get('eta', 0)
            size = info.get('size', 0)
            
            progress_bar = ProgressTracker.generate_progress_bar(
                int(progress),
                100,
                width=15
            )
            
            speed_str = ProgressTracker.format_speed(speed)
            eta_str = ProgressTracker.format_time(eta)
            size_str = ProgressTracker.format_bytes(size)
            
            # نمایش URL مختصر
            short_url = url[:40] + "..." if len(url) > 40 else url
            
            message += (
                f"**#{idx}** {progress_bar} {progress:.0f}%\n"
                f"   🔗 {short_url}\n"
                f"   ⚡ {speed_str}  |  ⏱️ {eta_str}\n"
                f"   📦 {size_str}\n\n"
            )
            
            total_progress += progress
            total_size += size
        
        # میانگین و خلاصه
        if active_count > 0:
            avg_progress = total_progress / active_count
            total_size_str = ProgressTracker.format_bytes(total_size)
            
            message += f"📊 **خلاصه:** {active_count} دانلود فعال\n"
            message += f"   میانگین: {avg_progress:.0f}%\n"
            message += f"   کل: {total_size_str}"
        
        return message
    
    @staticmethod
    async def generate_queue_status(
        queue_info: Dict
    ) -> str:
        """
        تولید پیام وضعیت صف
        
        Args:
            queue_info: اطلاعات صف
        
        Returns:
            پیام وضعیت صف
        """
        queue_length = queue_info.get('queue_length', 0)
        active = queue_info.get('active_downloads', 0)
        max_concurrent = queue_info.get('max_concurrent', 3)
        available = queue_info.get('available_slots', 0)
        
        # محاسبه زمان انتظار برآورد
        eta_minutes = (queue_length * 2)  # هر دانلود ~2 دقیقه
        
        status_bar = "█" * active + "░" * (max_concurrent - active)
        
        message = (
            f"📋 **وضعیت صف دانلود**\n\n"
            f"🔄 دانلود فعال: {status_bar} {active}/{max_concurrent}\n"
            f"⏳ در صف: {queue_length} دانلود\n"
            f"📊 دسترسی‌پذیر: {available} slot\n"
            f"⏱️ زمان انتظار برآورد: {eta_minutes} دقیقه\n"
        )
        
        return message
    
    @staticmethod
    async def generate_completion_summary(
        downloads_result: list,
        total_time: float
    ) -> str:
        """
        خلاصه دانلود‌های تکمیل‌شده
        
        Args:
            downloads_result: لیست نتایج
            total_time: کل زمان (seconds)
        
        Returns:
            خلاصه تکمیل‌شدگی
        """
        successful = sum(1 for r in downloads_result if r.get('status') == 'success')
        failed = sum(1 for r in downloads_result if r.get('status') == 'failed')
        
        time_str = ProgressTracker.format_time(int(total_time))
        
        message = (
            f"✅ **دانلود‌ها تکمیل شدند**\n\n"
            f"✅ موفق: {successful}/{len(downloads_result)}\n"
            f"❌ ناموفق: {failed}/{len(downloads_result)}\n"
            f"⏱️ کل زمان: {time_str}\n"
        )
        
        # اگر مواردی ناموفق باشند
        if failed > 0:
            message += f"\n⚠️ {failed} دانلود با مشکل مواجه شدند\n"
            for result in downloads_result:
                if result.get('status') == 'failed':
                    message += f"   • {result.get('url', 'Unknown')[:40]}...\n"
                    message += f"     {result.get('error', 'Unknown error')}\n"
        
        return message


class ProgressUpdater:
    """
    ارسال آپدیت‌های پیشرفت برای کاربران
    """
    
    def __init__(self, bot, chat_id: int, message_id: int):
        """
        Args:
            bot: Aiogram bot instance
            chat_id: Chat ID برای ارسال آپدیت
            message_id: Message ID برای edit
        """
        self.bot = bot
        self.chat_id = chat_id
        self.message_id = message_id
        self.last_update = None
    
    async def update_progress(
        self,
        downloads: Dict[str, Dict],
        force: bool = False
    ) -> None:
        """
        آپدیت پیشرفت (حداکثر هر 2 ثانیه)
        
        Args:
            downloads: تمام دانلود‌های فعال
            force: force update regardless of timing
        """
        now = datetime.utcnow()
        
        # محدود‌سازی آپدیت‌ها (هر 2 ثانیه)
        if not force and self.last_update:
            elapsed = (now - self.last_update).total_seconds()
            if elapsed < 2:
                return
        
        try:
            message = await ProgressTracker.generate_parallel_progress(downloads)
            
            await self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self.message_id,
                text=message,
                parse_mode="Markdown"
            )
            
            self.last_update = now
        
        except Exception as e:
            logger.error(f"[PROGRESS] Failed to update: {e}")


__all__ = [
    'ProgressTracker',
    'ProgressUpdater'
]
