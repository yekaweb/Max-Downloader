"""YouTube downloader module (yt-dlp) - Full implementation"""
import re
import asyncio
import os
from pathlib import Path
from typing import Optional, Callable
import logging

import yt_dlp

from ..base import BaseDownloader, MediaInfo
from .parser import parse_formats
from .config import YOUTUBE_CONFIG

logger = logging.getLogger(__name__)

YOUTUBE_REGEX = re.compile(
    r"(https?://)?(www\.)?(youtube\.com|youtu\.be|youtube-nocookie\.com)/"
)


class YouTubeDownloader(BaseDownloader):
    """YouTube downloader using yt-dlp library"""
    
    # Module metadata
    NAME = "YouTube"
    ICON = "▶️"
    SUPPORTED_DOMAINS = ["youtube.com", "youtu.be", "youtube-nocookie.com"]
    VERSION = "1.0.0"
    ENABLED = True
    PRIORITY = 100  # Highest priority - try YouTube first

    def __init__(self):
        self.ydl_opts = YOUTUBE_CONFIG.get("ydl_opts", {})

    @classmethod
    def can_handle(cls, url: str) -> bool:
        """Check if URL is a YouTube link"""
        return bool(YOUTUBE_REGEX.search(url))

    async def fetch_info(self, url: str) -> MediaInfo:
        """Fetch video metadata using yt-dlp"""
        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, self._extract_info, url)

            if not info:
                raise ValueError("Failed to extract video information")

            formats = parse_formats(info.get("formats", []))

            return MediaInfo(
                url=url,
                title=info.get("title", "Unknown"),
                duration=info.get("duration"),
                thumbnails=info.get("thumbnails", []),
                formats=formats,
                extra={
                    "video_id": info.get("id"),
                    "channel": info.get("channel"),
                    "upload_date": info.get("upload_date"),
                    "view_count": info.get("view_count"),
                    "like_count": info.get("like_count"),
                    "availability": info.get("availability", "public"),
                    "age_limit": info.get("age_limit", 0),
                },
            )
        except Exception as e:
            logger.error(f"Error fetching YouTube info for {url}: {e}")
            raise

    async def download(
        self,
        media_info: MediaInfo,
        output_path: str,
        format_id: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> str:
        """Download video using yt-dlp with optional progress tracking"""
        try:
            Path(output_path).mkdir(parents=True, exist_ok=True)

            opts = self.ydl_opts.copy()
            opts["outtmpl"] = os.path.join(output_path, "%(title)s.%(ext)s")

            if format_id:
                opts["format"] = format_id

            if progress_callback:
                opts["progress_hooks"] = [self._create_progress_hook(progress_callback)]

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._download_video, media_info.url, opts
            )

            return result

        except Exception as e:
            logger.error(f"Error downloading YouTube video: {e}")
            raise

    def _extract_info(self, url: str) -> dict:
        """Extract video info synchronously (runs in executor)"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            logger.error(f"yt-dlp extraction error: {e}")
            raise

    def _download_video(self, url: str, opts: dict) -> str:
        """Download video synchronously (runs in executor)"""
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                logger.info(f"Downloaded: {filename}")
                return filename
        except Exception as e:
            logger.error(f"yt-dlp download error: {e}")
            raise

    @staticmethod
    def _create_progress_hook(callback: Callable):
        """Create progress hook for yt-dlp"""

        def hook(d):
            if d["status"] == "downloading":
                progress = {
                    "status": "downloading",
                    "downloaded_bytes": d.get("downloaded_bytes", 0),
                    "total_bytes": d.get("total_bytes", 0),
                    "speed": d.get("speed"),
                    "eta": d.get("eta"),
                    "percent": d.get("_percent_str", "0%"),
                }
                try:
                    # Use asyncio.run_coroutine_threadsafe for thread safety
                    loop = asyncio.get_event_loop()
                    asyncio.run_coroutine_threadsafe(callback(progress), loop)
                except Exception as e:
                    logger.warning(f"Progress callback error: {e}")
            elif d["status"] == "finished":
                try:
                    loop = asyncio.get_event_loop()
                    asyncio.run_coroutine_threadsafe(
                        callback({"status": "finished"}), loop
                    )
                except Exception as e:
                    logger.warning(f"Finished callback error: {e}")

        return hook


# Auto-register module
from modules import register_module

register_module("youtube", YouTubeDownloader())

__all__ = ["YouTubeDownloader"]
