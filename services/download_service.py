"""Download service - orchestrates download flow and integrates module registry.

This service delegates media-info lookups and downloads to the pluggable
downloader modules (modules package). It also exposes a small ProgressUpdater
helper used by tasks and handlers to edit progress messages with throttling.
"""

import asyncio
import time
from typing import Optional
from loguru import logger

from modules import get_downloader, get_all_downloaders


class ProgressUpdater:
    """Throttled progress message updater for preventing Telegram rate limits.

    One instance can be reused per logical download to serialize edits.
    """

    def __init__(self, throttle_interval: int = 3):
        self._lock = asyncio.Lock()
        self._last_update = 0.0
        self._throttle_interval = throttle_interval
        self._message = None

    async def set_message(self, message) -> None:
        """Store aiogram message object used for edits."""
        self._message = message

    async def update_progress(
        self,
        title: str,
        progress_percent: float,
        downloaded_mb: float,
        total_mb: float,
        speed_mbps: float,
        eta_seconds: int,
        queue_position: int = 0,
        phase: str = "download",
    ) -> bool:
        async with self._lock:
            now = time.time()
            if now - self._last_update < self._throttle_interval:
                return False

            if not self._message:
                logger.debug("ProgressUpdater: no message set")
                return False

            try:
                from utils.progress import generate_progress_message

                text = generate_progress_message(
                    title=title,
                    progress_percent=progress_percent,
                    downloaded_mb=downloaded_mb,
                    total_mb=total_mb,
                    speed_mbps=speed_mbps,
                    eta_seconds=eta_seconds,
                    queue_position=queue_position,
                    phase=phase,
                    use_html=True,
                )

                await self._message.edit_text(text, parse_mode="HTML")
                self._last_update = now
                return True
            except Exception as e:
                logger.debug(f"ProgressUpdater update failed: {e}")
                return False


class DownloadService:
    """Facade around the downloader modules.

    Methods here are thin wrappers that locate the correct module and call
    into it. This keeps handlers and tasks decoupled from module internals.
    """

    def __init__(self):
        # Nothing to initialize; module registry is global in `modules`
        pass

    async def get_media_info(self, url: str):
        """Return MediaInfo for a URL by delegating to the appropriate module.

        Raises ValueError if no handler is available.
        """
        downloader = get_downloader(url)
        if not downloader:
            raise ValueError("No downloader available for this URL")

        return await downloader.get_media_info(url)

    async def download(
        self,
        url: str,
        format_id: str,
        output_dir: str,
        db: Optional[object] = None,
        file_service: Optional[object] = None,
        chat_id: Optional[int] = None,
        progress_callback: Optional[callable] = None,
    ):
        """Download media and optionally upload to Telegram and cache result.

        If a cached Telegram `file_id` exists for the URL+format, returns a
        dict with `cached=True` and the `telegram_file_id`.

        Otherwise performs module download, uploads via `file_service` and
        creates a `CachedDownload` entry when `db` is provided.
        """
        downloader = get_downloader(url)
        if not downloader:
            raise ValueError("No downloader available for this URL")

        # If db and file_service provided, try to find cached entry first
        if db is not None and file_service is not None:
            try:
                from database.repositories.cached_download_repo import CachedDownloadRepository

                repo = CachedDownloadRepository(db)
                cached = await repo.find_valid_by_url(url)
                if cached:
                    # Return the most recent cached entry
                    entry = cached[0]
                    first_quality = entry.qualities[0] if entry.qualities else None
                    return {
                        "cached": True,
                        "telegram_file_id": first_quality.telegram_file_id if first_quality else None,
                        "cached_entry": entry,
                    }
            except Exception:
                # If repo missing or error, continue with fresh download
                pass

        # Perform actual download via module
        result = await downloader.download(
            url=url,
            format_id=format_id,
            output_dir=output_dir,
            progress_callback=progress_callback,
        )

        # If file_service and db provided, upload and create cache record
        if file_service is not None and db is not None and chat_id is not None:
            try:
                # Upload to Telegram via file_service
                file_id = await file_service.upload_to_telegram(
                    result.file_path, chat_id, caption=result.filename, progress_callback=progress_callback
                )

                if file_id:
                    # Persist cached download record
                    from database.repositories.cached_download_repo import CachedDownloadRepository

                    repo = CachedDownloadRepository(db)
                    await repo.create_from_upload(
                        source_url=url,
                        source_platform=getattr(downloader, "NAME", "unknown"),
                        media_title=result.filename,
                        media_duration=getattr(result, "duration", None) or 0,
                        media_uploader="",
                        telegram_file_id=file_id,
                        file_size=result.filesize,
                        file_type=result.format_info.ext,
                        quality=result.format_info.quality_label,
                        format_codec=result.format_info.codec,
                        format_container=result.format_info.ext,
                        resolution_width=getattr(result.format_info, "width", None),
                        resolution_height=getattr(result.format_info, "height", None),
                    )

                    # Clean up local file
                    try:
                        await file_service.delete_file(result.file_path)
                    except Exception:
                        pass

                    return {"cached": False, "telegram_file_id": file_id}
            except Exception:
                # swallow upload/cache errors but still return raw result
                return {"cached": False, "download_result": result}

        return {"cached": False, "download_result": result}

    async def list_supported_platforms(self) -> list[str]:
        """Return list of supported platform keys (for user messages)."""
        return list(get_all_downloaders().keys())


__all__ = ["DownloadService", "ProgressUpdater"]

