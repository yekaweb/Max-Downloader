"""Instagram downloader module - Download Reels, Posts, and Stories using yt-dlp & instagrapi"""
import os
import re
import asyncio
import logging
from pathlib import Path
from typing import Optional, Callable, List

import yt_dlp

from ..base import BaseDownloader, MediaInfo

logger = logging.getLogger(__name__)

INSTAGRAM_REGEX = re.compile(
    r"(https?://)?(www\.)?(instagram\.com|insta\.io)/(p|reel|tv|stories)/[A-Za-z0-9\-_]+"
)


class InstagramDownloader(BaseDownloader):
    """
    Instagram downloader supporting Reels, Posts, and Videos.
    Primary engine: yt-dlp (reliable, no login required for public posts).
    Secondary engine: instagrapi (for stories / private posts if session configured).
    """

    NAME = "Instagram"
    ICON = "📸"
    SUPPORTED_DOMAINS = ["instagram.com", "insta.io"]
    VERSION = "2.0.0"
    ENABLED = True
    PRIORITY = 85

    def __init__(self):
        self.ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
        }

    @classmethod
    def can_handle(cls, url: str) -> bool:
        """Check if URL is an Instagram link"""
        return bool(INSTAGRAM_REGEX.search(url))

    async def fetch_info(self, url: str) -> MediaInfo:
        """Fetch Instagram media metadata"""
        normalized_url = self._normalize_url(url)
        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, self._extract_info, normalized_url)

            if not info:
                raise ValueError("Failed to extract Instagram media information")

            formats = []
            if "formats" in info:
                for f in info["formats"]:
                    formats.append({
                        "format_id": f.get("format_id"),
                        "ext": f.get("ext", "mp4"),
                        "resolution": f"{f.get('width', 0)}x{f.get('height', 0)}",
                        "size_mb": (f.get("filesize", 0) or 0) / (1024 * 1024),
                    })

            return MediaInfo(
                url=normalized_url,
                title=info.get("title", f"Instagram Media ({info.get('id', '')})"),
                duration=info.get("duration", 0),
                thumbnails=info.get("thumbnails", []),
                formats=formats,
                extra={
                    "platform": "instagram",
                    "uploader": info.get("uploader"),
                    "media_id": info.get("id"),
                    "like_count": info.get("like_count"),
                },
            )
        except Exception as e:
            logger.error(f"Error fetching Instagram info for {url}: {e}")
            raise

    async def download(
        self,
        media_info: MediaInfo,
        output_path: str,
        format_id: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> str:
        """Download Instagram media using yt-dlp"""
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
            logger.error(f"Error downloading Instagram media: {e}")
            raise

    def _extract_info(self, url: str) -> dict:
        """Extract info synchronously"""
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    def _download_video(self, url: str, opts: dict) -> str:
        """Download video synchronously"""
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base = os.path.splitext(filename)[0]
            import glob
            matches = [f for f in glob.glob(f"{base}.*") if os.path.isfile(f)]
            if matches:
                return max(matches, key=os.path.getsize)
            return filename

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
                    loop = asyncio.get_event_loop()
                    asyncio.run_coroutine_threadsafe(callback(progress), loop)
                except Exception as e:
                    logger.warning(f"Progress callback error: {e}")
            elif d["status"] == "finished":
                try:
                    loop = asyncio.get_event_loop()
                    asyncio.run_coroutine_threadsafe(callback({"status": "finished"}), loop)
                except Exception as e:
                    logger.warning(f"Finished callback error: {e}")
        return hook

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize Instagram URL"""
        url = url.split("?")[0].rstrip("/")
        if not url.startswith("http"):
            url = f"https://{url}"
        return url


# Auto-register module
from modules import register_module
register_module("instagram", InstagramDownloader())

__all__ = ["InstagramDownloader"]
