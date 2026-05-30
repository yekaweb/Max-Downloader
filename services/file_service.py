"""File service - Pyrogram file upload and management"""
import os
import hashlib
import logging
from pathlib import Path
from typing import Optional, Callable, Union
from datetime import datetime

import aiofiles
from pyrogram import Client

logger = logging.getLogger(__name__)


class FileService:
    """Handles file operations: upload to Telegram via Pyrogram, local caching, cleanup"""

    def __init__(
        self,
        temp_dir: str,
        cache_dir: str,
        pyrogram_client: Optional[Client] = None,
    ):
        """
        Initialize FileService

        Args:
            temp_dir: Directory for temporary downloads
            cache_dir: Directory for cached files
            pyrogram_client: Pyrogram Client instance for large file uploads
        """
        self.temp_dir = Path(temp_dir)
        self.cache_dir = Path(cache_dir)
        self.pyrogram_client = pyrogram_client

        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def get_file_hash(self, file_path: Union[str, Path]) -> str:
        """Calculate SHA256 hash of file"""
        if isinstance(file_path, str):
            file_path = Path(file_path)

        sha256 = hashlib.sha256()
        async with aiofiles.open(file_path, "rb") as f:
            while True:
                chunk = await f.read(8192)
                if not chunk:
                    break
                sha256.update(chunk)
        return sha256.hexdigest()

    async def is_file_cached(self, file_hash: str) -> bool:
        """Check if file is already cached"""
        cache_file = self.cache_dir / f"{file_hash}.json"
        return cache_file.exists()

    async def cache_file_info(
        self, file_path: Union[str, Path], file_id: str, file_hash: str
    ) -> None:
        """Cache file metadata (Telegram file_id)"""
        import json

        if isinstance(file_path, str):
            file_path = Path(file_path)

        file_info = {
            "file_id": file_id,
            "file_hash": file_hash,
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "cached_at": datetime.utcnow().isoformat(),
        }

        cache_file = self.cache_dir / f"{file_hash}.json"
        async with aiofiles.open(cache_file, "w") as f:
            await f.write(json.dumps(file_info, indent=2))
        logger.info(f"Cached file info: {file_hash}")

    async def get_cached_file_id(self, file_hash: str) -> Optional[str]:
        """Get cached Telegram file_id for a hash"""
        import json

        cache_file = self.cache_dir / f"{file_hash}.json"
        if not cache_file.exists():
            return None

        try:
            async with aiofiles.open(cache_file, "r") as f:
                content = await f.read()
                data = json.loads(content)
                return data.get("file_id")
        except Exception as e:
            logger.error(f"Error reading cache: {e}")
            return None

    async def upload_to_telegram(
        self,
        file_path: Union[str, Path],
        chat_id: int,
        caption: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> Optional[str]:
        """
        Upload file to Telegram via Pyrogram (supports up to 4GB).

        Args:
            file_path: Path to file to upload
            chat_id: Telegram chat_id to upload to
            caption: Optional caption for the file
            progress_callback: Optional async callback for upload progress

        Returns:
            Telegram file_id if successful, None otherwise
        """
        if not self.pyrogram_client:
            logger.error("Pyrogram client not initialized")
            return None

        if isinstance(file_path, str):
            file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        try:
            # Get file hash for caching
            file_hash = await self.get_file_hash(file_path)

            # Check if already cached
            cached_id = await self.get_cached_file_id(file_hash)
            if cached_id:
                logger.info(f"Using cached file_id for: {file_path.name}")
                return cached_id

            logger.info(f"Uploading file to Telegram: {file_path.name}")

            # Upload file
            message = await self.pyrogram_client.send_document(
                chat_id=chat_id,
                document=str(file_path),
                caption=caption or file_path.name,
                progress=progress_callback,
            )

            file_id = message.document.file_id
            file_unique_id = message.document.file_unique_id

            # Cache the file_id
            await self.cache_file_info(file_path, file_id, file_hash)

            logger.info(f"Successfully uploaded: {file_path.name} → {file_id[:20]}...")
            return file_id

        except Exception as e:
            logger.error(f"Pyrogram upload error: {e}")
            return None

    async def get_file_from_telegram(
        self,
        file_id: str,
        save_path: Union[str, Path],
        progress_callback: Optional[Callable] = None,
    ) -> Optional[str]:
        """
        Download file from Telegram using file_id.

        Args:
            file_id: Telegram file_id
            save_path: Path to save file
            progress_callback: Optional async callback for download progress

        Returns:
            Path to downloaded file if successful, None otherwise
        """
        if not self.pyrogram_client:
            logger.error("Pyrogram client not initialized")
            return None

        try:
            logger.info(f"Downloading file from Telegram: {file_id[:20]}...")

            path = await self.pyrogram_client.download_media(
                file_id,
                file_name=str(save_path),
                progress=progress_callback,
            )

            logger.info(f"Successfully downloaded to: {path}")
            return path

        except Exception as e:
            logger.error(f"Pyrogram download error: {e}")
            return None

    async def cleanup_old_files(self, max_age_hours: int = 48) -> int:
        """
        Clean up old cached files and metadata.

        Args:
            max_age_hours: Remove files older than this many hours

        Returns:
            Number of files removed
        """
        import time

        cutoff = time.time() - (max_age_hours * 3600)
        removed = 0

        try:
            for file_path in self.cache_dir.glob("*"):
                if file_path.stat().st_mtime < cutoff:
                    file_path.unlink()
                    removed += 1

            logger.info(f"Cleaned up {removed} old files")
            return removed

        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return 0

    async def get_file_size(self, file_path: Union[str, Path]) -> int:
        """Get file size in bytes"""
        if isinstance(file_path, str):
            file_path = Path(file_path)

        if file_path.exists():
            return file_path.stat().st_size
        return 0

    async def delete_file(self, file_path: Union[str, Path]) -> bool:
        """Delete a file"""
        if isinstance(file_path, str):
            file_path = Path(file_path)

        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False


__all__ = ["FileService"]
