"""
Cobalt API Service for DLBot.
Provides Tier-2 Fallback downloading via Cobalt API instances.
Supports multiple instance rotation, streaming downloads, and media metadata extraction.
"""

import os
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_COBALT_INSTANCES = [
    "https://api.cobalt.tools",
    "https://cobalt-api.kwiatekm.pl",
    "https://api.server.im",
    "https://cobalt.xy2.dev",
]


class CobaltService:
    """
    Client for interacting with Cobalt API instances.
    """

    def __init__(self, instances: Optional[List[str]] = None, timeout: int = 30):
        self.instances = instances or DEFAULT_COBALT_INSTANCES
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def get_media_stream_url(
        self,
        url: str,
        video_quality: str = "720",
        audio_only: bool = False,
        codec: str = "h264",
    ) -> Dict[str, Any]:
        """
        Request media stream URL from Cobalt API across instances with failover.
        """
        payload = {
            "url": url,
            "videoQuality": str(video_quality) if video_quality != "4k" else "2160",
            "youtubeVideoCodec": codec if codec in ["h264", "av1", "vp9"] else "h264",
            "downloadMode": "audio" if audio_only else "auto",
            "audioFormat": "mp3" if audio_only else "best",
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DLBot-Titan/2.0",
        }

        last_error = None
        for instance in self.instances:
            endpoint = f"{instance.rstrip('/')}/"
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.post(endpoint, json=payload, headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            status = data.get("status")
                            if status in ["stream", "redirect", "tunnel"]:
                                return {
                                    "success": True,
                                    "url": data.get("url"),
                                    "filename": data.get("filename", "video.mp4"),
                                    "status": status,
                                    "instance": instance,
                                }
                            elif status == "picker":
                                items = data.get("picker", [])
                                if items:
                                    first_item = items[0]
                                    return {
                                        "success": True,
                                        "url": first_item.get("url"),
                                        "filename": data.get("filename", "media.mp4"),
                                        "status": "picker",
                                        "instance": instance,
                                    }
                            elif status == "error":
                                err_text = data.get("error", {}).get("code", "unknown_error")
                                logger.warning(f"Cobalt {instance} returned error: {err_text}")
                                last_error = err_text
                        else:
                            last_error = f"HTTP {resp.status}"
            except Exception as e:
                logger.debug(f"Cobalt instance {instance} failed: {e}")
                last_error = str(e)
                continue

        return {"success": False, "error": last_error or "All Cobalt instances failed"}

    async def download_file(
        self,
        stream_url: str,
        output_path: Path,
        progress_callback: Optional[Callable[[float, float, float, float, int], Any]] = None,
    ) -> Path:
        """
        Download media from stream_url directly to output_path with progress updates.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(stream_url) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Cobalt stream returned HTTP {resp.status}")

                total_bytes = int(resp.headers.get("Content-Length", 0))
                downloaded_bytes = 0
                chunk_size = 1024 * 64  # 64 KB chunks
                start_time = asyncio.get_event_loop().time()

                with open(output_path, "wb") as f:
                    while True:
                        chunk = await resp.content.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded_bytes += len(chunk)

                        if progress_callback and total_bytes > 0:
                            elapsed = asyncio.get_event_loop().time() - start_time
                            speed_mbps = (downloaded_bytes / (1024 * 1024)) / (elapsed if elapsed > 0 else 1)
                            percent = (downloaded_bytes / total_bytes) * 100
                            dl_mb = downloaded_bytes / (1024 * 1024)
                            tot_mb = total_bytes / (1024 * 1024)
                            eta = int((total_bytes - downloaded_bytes) / (speed_mbps * 1024 * 1024)) if speed_mbps > 0 else 0
                            try:
                                if asyncio.iscoroutinefunction(progress_callback):
                                    await progress_callback(percent, dl_mb, tot_mb, speed_mbps, eta)
                                else:
                                    progress_callback(percent, dl_mb, tot_mb, speed_mbps, eta)
                            except Exception:
                                pass

        return output_path


cobalt_service = CobaltService()

__all__ = ["CobaltService", "cobalt_service"]
