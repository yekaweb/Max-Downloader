"""
Multi-Engine Waterfall Download Service for DLBot.
Implements a 3-tier resilient downloading strategy:
  - Tier 1: yt-dlp Native Engine (with PO-Token, Mobile Player Client Spoofing & Session Cookies)
  - Tier 2: Cobalt Multi-Instance API Engine
  - Tier 3: Direct Stream Extractor Fallback
"""

import os
import glob
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Callable, Tuple

import yt_dlp
from services.potoken_service import po_token_service
from services.cobalt_service import cobalt_service
from utils.proxy_manager import get_random_proxy

logger = logging.getLogger(__name__)

COOKIE_FILE = Path("/root/Max-Downloader/cookies.txt")

_BASE_YTDLP_CONFIG = {
    'socket_timeout': 30,
    'noplaylist': True,
    'cookiefile': str(COOKIE_FILE) if COOKIE_FILE.exists() else None,
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web_safari', 'mweb', 'ios'],
            'lang': ['en', 'fa'],
        }
    },
    'http_headers': {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/128.0.0.0 Safari/537.36'
        ),
        'Accept-Language': 'en-US,en;q=0.9,fa;q=0.8',
    },
    'retries': 5,
    'fragment_retries': 5,
    'skip_unavailable_fragments': True,
}


class WaterfallDownloadService:
    """
    Orchestrates download attempts across multiple tiers to ensure zero-failure execution.
    """

    def __init__(self, temp_dir: str = "temp_downloads"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def execute_download(
        self,
        url: str,
        format_type: str = "video",
        quality: str = "720",
        codec: str = "h264",
        audio_format: Optional[Dict[str, str]] = None,
        audio_lang: Optional[str] = None,
        max_filesize: Optional[int] = None,
        progress_callback: Optional[Callable] = None,
    ) -> Tuple[Optional[str], str]:
        """
        Execute waterfall download.
        Returns: (downloaded_file_path, engine_used)
        """
        # ----------------------------------------------------
        # TIER 1: yt-dlp Native Engine with PO-Token & Spoofing
        # ----------------------------------------------------
        logger.info(f"[Waterfall] Starting Tier 1 (yt-dlp) for {url}")
        try:
            file_path = await self._download_tier1_ytdlp(
                url=url,
                format_type=format_type,
                quality=quality,
                codec=codec,
                audio_format=audio_format,
                audio_lang=audio_lang,
                max_filesize=max_filesize,
                progress_callback=progress_callback,
            )
            if file_path and os.path.exists(file_path):
                logger.info(f"[Waterfall] Tier 1 succeeded: {file_path}")
                return file_path, "yt-dlp (Native)"
        except Exception as tier1_err:
            logger.warning(f"[Waterfall] Tier 1 failed: {tier1_err}. Falling back to Tier 2 (Cobalt)...")

        # ----------------------------------------------------
        # TIER 2: Cobalt Multi-Instance Engine
        # ----------------------------------------------------
        logger.info(f"[Waterfall] Starting Tier 2 (Cobalt API) for {url}")
        try:
            file_path = await self._download_tier2_cobalt(
                url=url,
                format_type=format_type,
                quality=quality,
                codec=codec,
                progress_callback=progress_callback,
            )
            if file_path and os.path.exists(file_path):
                logger.info(f"[Waterfall] Tier 2 succeeded: {file_path}")
                return file_path, "Cobalt API (Cluster)"
        except Exception as tier2_err:
            logger.warning(f"[Waterfall] Tier 2 failed: {tier2_err}. Falling back to Tier 3 (Direct)...")

        # ----------------------------------------------------
        # TIER 3: Direct Stream Fallback
        # ----------------------------------------------------
        logger.info(f"[Waterfall] Starting Tier 3 (Direct Stream) for {url}")
        try:
            file_path = await self._download_tier3_direct(
                url=url,
                format_type=format_type,
                progress_callback=progress_callback,
            )
            if file_path and os.path.exists(file_path):
                logger.info(f"[Waterfall] Tier 3 succeeded: {file_path}")
                return file_path, "Direct Stream"
        except Exception as tier3_err:
            logger.error(f"[Waterfall] All 3 download tiers failed for {url}. Last error: {tier3_err}")
            raise RuntimeError(f"All download engines exhausted for this URL: {tier3_err}")

        return None, "None"

    async def _download_tier1_ytdlp(
        self,
        url: str,
        format_type: str,
        quality: str,
        codec: str,
        audio_format: Optional[Dict[str, str]],
        audio_lang: Optional[str],
        max_filesize: Optional[int],
        progress_callback: Optional[Callable],
    ) -> Optional[str]:
        """Tier 1 yt-dlp implementation."""
        ydl_opts = {
            **_BASE_YTDLP_CONFIG,
            "quiet": True,
            "no_warnings": True,
            "outtmpl": str(self.temp_dir / "%(title)s.%(ext)s"),
            "merge_output_format": "mp4",
        }

        # Inject PO-Token if available
        ydl_opts = po_token_service.inject_into_ydl_opts(ydl_opts)

        if max_filesize:
            ydl_opts["max_filesize"] = max_filesize

        proxy = get_random_proxy()
        if proxy:
            ydl_opts['proxy'] = proxy

        if format_type == "video":
            quality_map = {
                "4k": 2160,
                "1440": 1440,
                "1080": 1080,
                "720": 720,
                "480": 480,
                "360": 360,
                "240": 240,
            }
            height = quality_map.get(quality, 720)
            audio_sel = f"bestaudio[language={audio_lang}]/bestaudio" if audio_lang else "bestaudio"

            if codec == "h264":
                ydl_opts["format"] = (
                    f"bestvideo[height<={height}][vcodec*=avc]+{audio_sel}[ext=m4a]"
                    f"/bestvideo[height<={height}][ext=mp4]+{audio_sel}"
                    f"/best[height<={height}]"
                )
            elif codec == "av1":
                ydl_opts["format"] = (
                    f"bestvideo[height<={height}][vcodec^=av01]+{audio_sel}"
                    f"/best[height<={height}]"
                )
            elif codec == "vp9":
                ydl_opts["format"] = (
                    f"bestvideo[height<={height}][vcodec^=vp09]+{audio_sel}"
                    f"/bestvideo[height<={height}][vcodec^=vp9]+{audio_sel}"
                    f"/best[height<={height}]"
                )
            else:
                ydl_opts["format"] = (
                    f"bestvideo[height<={height}]+{audio_sel}"
                    f"/best[height<={height}]"
                )
        else:
            audio_fmt = audio_format or {"format": "mp3", "bitrate": "128"}
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_fmt.get("format", "mp3"),
                "preferredquality": audio_fmt.get("bitrate", "128"),
            }]

        loop = asyncio.get_running_loop()

        def progress_hook(d):
            if d['status'] == 'downloading' and progress_callback:
                try:
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    speed_bytes = d.get('speed', 0) or 0
                    eta_sec = d.get('eta', 0) or 0
                    percent = (downloaded_bytes / total_bytes * 100) if total_bytes else 0
                    dl_mb = downloaded_bytes / (1024 * 1024)
                    tot_mb = total_bytes / (1024 * 1024)
                    speed_mbps = speed_bytes / (1024 * 1024)

                    if asyncio.iscoroutinefunction(progress_callback):
                        asyncio.run_coroutine_threadsafe(
                            progress_callback(percent, dl_mb, tot_mb, speed_mbps, eta_sec),
                            loop
                        )
                    else:
                        progress_callback(percent, dl_mb, tot_mb, speed_mbps, eta_sec)
                except Exception:
                    pass

        ydl_opts["progress_hooks"] = [progress_hook]

        def _run_extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                raw_name = ydl.prepare_filename(info)
                base = os.path.splitext(raw_name)[0]
                matches = [f for f in glob.glob(f"{base}.*") if os.path.isfile(f)]
                if matches:
                    return max(matches, key=os.path.getsize)
                return raw_name

        return await loop.run_in_executor(None, _run_extract)

    async def _download_tier2_cobalt(
        self,
        url: str,
        format_type: str,
        quality: str,
        codec: str,
        progress_callback: Optional[Callable],
    ) -> Optional[str]:
        """Tier 2 Cobalt implementation."""
        audio_only = (format_type == "audio")
        res = await cobalt_service.get_media_stream_url(
            url=url,
            video_quality=quality,
            audio_only=audio_only,
            codec=codec,
        )

        if not res.get("success") or not res.get("url"):
            raise RuntimeError(f"Cobalt extraction failed: {res.get('error')}")

        stream_url = res["url"]
        filename = res.get("filename") or f"cobalt_download_{int(asyncio.get_event_loop().time())}.mp4"
        out_file = self.temp_dir / filename

        return str(await cobalt_service.download_file(
            stream_url=stream_url,
            output_path=out_file,
            progress_callback=progress_callback,
        ))

    async def _download_tier3_direct(
        self,
        url: str,
        format_type: str,
        progress_callback: Optional[Callable],
    ) -> Optional[str]:
        """Tier 3 Direct/Generic Stream implementation."""
        ydl_opts = {
            'socket_timeout': 30,
            'noplaylist': True,
            'format': 'best',
            'outtmpl': str(self.temp_dir / "%(title)s.%(ext)s"),
            'quiet': True,
        }
        loop = asyncio.get_running_loop()

        def _run_generic():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)

        return await loop.run_in_executor(None, _run_generic)


waterfall_download_service = WaterfallDownloadService()

__all__ = ["WaterfallDownloadService", "waterfall_download_service"]
