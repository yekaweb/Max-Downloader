"""Download service - orchestrates download flow"""

import asyncio
import time
from typing import Optional, Dict, Any
from loguru import logger


class ProgressUpdater:
    """
    Throttled progress message updater for preventing Telegram rate limits.
    
    Provides async-safe updates with configurable throttle interval.
    One instance per user to prevent concurrent message edits.
    """
    
    def __init__(self, throttle_interval: int = 3):
        """
        Initialize progress updater with throttling.
        
        Args:
            throttle_interval: Minimum seconds between progress updates (default 3)
        """
        self._lock = asyncio.Lock()
        self._last_update = 0
        self._throttle_interval = throttle_interval
        self._message = None
        self._chat_id = None
        self._message_id = None
    
    async def set_message(self, message, chat_id: int, message_id: int) -> None:
        """Store message reference for later updates"""
        self._message = message
        self._chat_id = chat_id
        self._message_id = message_id
    
    async def update_progress(
        self,
        title: str,
        progress_percent: float,
        downloaded_mb: float,
        total_mb: float,
        speed_mbps: float,
        eta_seconds: int,
        queue_position: int = 0,
        phase: str = "download"
    ) -> bool:
        """
        Update progress message with throttling to prevent message flood.
        
        Args:
            title: Download title
            progress_percent: Progress percentage (0-100)
            downloaded_mb: Downloaded size in MB
            total_mb: Total size in MB
            speed_mbps: Download speed in MB/s
            eta_seconds: Estimated time remaining in seconds
            queue_position: Position in download queue (optional)
            phase: Current phase ("download", "upload", "processing")
        
        Returns:
            True if message was updated, False if throttled
        """
        async with self._lock:
            current_time = time.time()
            
            # Check if enough time has passed since last update
            if current_time - self._last_update < self._throttle_interval:
                return False
            
            if not self._message:
                logger.warning("Progress message not set - cannot update")
                return False
            
            try:
                # Import here to avoid circular imports
                from utils.progress import generate_progress_message
                
                new_text = generate_progress_message(
                    title=title,
                    progress_percent=progress_percent,
                    downloaded_mb=downloaded_mb,
                    total_mb=total_mb,
                    speed_mbps=speed_mbps,
                    eta_seconds=eta_seconds,
                    queue_position=queue_position,
                    phase=phase,
                    use_html=True
                )
                
                # Edit message in Telegram
                await self._message.edit_text(
                    new_text,
                    parse_mode="HTML"
                )
                
                self._last_update = current_time
                logger.debug(f"Progress updated: {progress_percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f}MB)")
                return True
                
            except Exception as e:
                logger.warning(f"Progress update failed: {e}")
                return False


class DownloadService:
    def __init__(self):
        self.modules = {}

    async def download(self, url: str, quality: str = "best"):
        """Download media from URL"""
        # Find appropriate module
        for module in self.modules.values():
            if module.can_handle(url):
                info = await module.fetch_info(url)
                return info
        
        raise ValueError(f"No module can handle URL: {url}")

__all__ = ["DownloadService", "ProgressUpdater"]

