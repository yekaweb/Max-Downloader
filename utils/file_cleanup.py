"""
File Cleanup Utilities
Handle deletion of downloaded files after successful Telegram upload
"""

import os
import asyncio
from pathlib import Path
from typing import Optional
from loguru import logger
from config import settings


class FileCleanup:
    """Manage temporary file cleanup"""
    
    @staticmethod
    async def cleanup_after_upload(file_path: str, delay_seconds: int = 5) -> bool:
        """
        Delete file after successful upload to Telegram
        
        Args:
            file_path: Path to file to delete
            delay_seconds: Delay before deletion (give Telegram time to process)
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Convert to Path object
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.warning(f"File not found for cleanup: {file_path}")
                return False
            
            # Wait before deletion to ensure upload completed
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)
            
            # Delete file
            file_path.unlink()
            logger.info(f"✅ Cleaned up file: {file_path} ({file_path.stat().st_size / 1024 / 1024:.1f}MB)")
            
            return True
            
        except FileNotFoundError:
            logger.warning(f"File already deleted: {file_path}")
            return True
        except PermissionError:
            logger.error(f"❌ Permission denied deleting file: {file_path}")
            return False
        except Exception as e:
            logger.error(f"❌ Error deleting file {file_path}: {e}")
            return False
    
    @staticmethod
    async def cleanup_temp_directory(max_age_hours: Optional[int] = None) -> int:
        """
        Clean up old temp files from download directory
        
        Args:
            max_age_hours: Delete files older than this (None = use config)
        
        Returns:
            Number of files deleted
        """
        try:
            if max_age_hours is None:
                max_age_hours = settings.MAX_FILE_AGE_HOURS
            
            temp_dir = Path(settings.TEMP_DOWNLOAD_DIR)
            if not temp_dir.exists():
                return 0
            
            import time
            current_time = time.time()
            deleted_count = 0
            
            for file_path in temp_dir.glob("*"):
                if file_path.is_file():
                    # Check file age
                    file_age_hours = (current_time - file_path.stat().st_mtime) / 3600
                    
                    if file_age_hours > max_age_hours:
                        try:
                            file_size_mb = file_path.stat().st_size / 1024 / 1024
                            file_path.unlink()
                            deleted_count += 1
                            logger.info(f"🗑️ Cleaned old temp file: {file_path.name} "
                                      f"({file_age_hours:.1f}h old, {file_size_mb:.1f}MB)")
                        except Exception as e:
                            logger.error(f"Error deleting old file {file_path}: {e}")
            
            if deleted_count > 0:
                logger.info(f"✅ Cleanup: Deleted {deleted_count} old temp files")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during temp directory cleanup: {e}")
            return 0
    
    @staticmethod
    def get_temp_file_size_mb(file_path: str) -> float:
        """Get file size in MB"""
        try:
            return Path(file_path).stat().st_size / 1024 / 1024
        except Exception:
            return 0.0
    
    @staticmethod
    def get_temp_directory_size_mb() -> float:
        """Get total size of temp directory in MB"""
        try:
            temp_dir = Path(settings.TEMP_DOWNLOAD_DIR)
            if not temp_dir.exists():
                return 0.0
            
            total_size = sum(f.stat().st_size for f in temp_dir.glob("*") if f.is_file())
            return total_size / 1024 / 1024
        except Exception:
            return 0.0


# Async cleanup scheduler (runs periodically)
async def start_cleanup_scheduler(interval_minutes: int = 60):
    """Start background cleanup scheduler"""
    logger.info(f"🧹 Starting cleanup scheduler (every {interval_minutes} minutes)")
    
    while True:
        try:
            await asyncio.sleep(interval_minutes * 60)
            deleted = await FileCleanup.cleanup_temp_directory()
            if deleted > 0:
                logger.info(f"🧹 Scheduled cleanup: {deleted} files removed")
        except Exception as e:
            logger.error(f"Cleanup scheduler error: {e}")


__all__ = ["FileCleanup", "start_cleanup_scheduler"]
