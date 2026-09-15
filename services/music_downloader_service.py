"""
Full Music Downloader Service.
Searches and downloads full 320kbps studio tracks for recognized songs.
Supports multi-source fallback: SoundCloud -> YouTube.
"""

import os
import glob
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import yt_dlp

logger = logging.getLogger(__name__)


class MusicDownloaderService:
    """
    Downloads full studio MP3 tracks for recognized music tracks.
    """

    async def download_track_by_query(
        self,
        query: str,
        output_dir: Path,
        custom_filename: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Search and download full studio version of a song using SoundCloud / YouTube search.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = custom_filename or "full_track"
        out_tmpl = str(output_dir / f"{safe_name}_%(id)s.%(ext)s")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": out_tmpl,
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 20,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                },
            ],
        }

        loop = asyncio.get_running_loop()

        def _try_search(search_prefix: str, search_query: str):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    search_term = f"{search_prefix}:{search_query}"
                    info = ydl.extract_info(search_term, download=True)
                    if not info:
                        return None

                    entries = info.get("entries")
                    entry = entries[0] if entries else info
                    if not entry:
                        return None

                    target_id = entry.get("id")
                    matches = [f for f in glob.glob(str(output_dir / f"{safe_name}_{target_id}.mp3"))]
                    if not matches:
                        matches = [f for f in glob.glob(str(output_dir / f"{safe_name}_*.mp3"))]

                    file_path = matches[0] if matches else None
                    if file_path and os.path.exists(file_path):
                        return {
                            "file_path": file_path,
                            "title": entry.get("title", query),
                            "artist": entry.get("uploader", entry.get("channel", "Music")),
                            "duration": entry.get("duration", 0),
                            "thumbnail": entry.get("thumbnail"),
                        }
            except Exception as e:
                logger.warning(f"[MusicDownloader] Source '{search_prefix}' failed for '{query}': {e}")
            return None

        def _sync_download():
            # 1. Try SoundCloud first (very fast, zero bot-checks, clean studio audio)
            res = _try_search("scsearch1", query)
            if res:
                return res

            # 2. Try YouTube search
            res = _try_search("ytsearch1", f"{query} audio")
            if res:
                return res

            # 3. Try broader YouTube search
            res = _try_search("ytsearch1", query)
            if res:
                return res

            return None

        try:
            res = await loop.run_in_executor(None, _sync_download)
            if res and res.get("file_path") and os.path.exists(res["file_path"]):
                return res
            return None
        except Exception as e:
            logger.error(f"[MusicDownloader] Failed to download track for query '{query}': {e}")
            return None


music_downloader_service = MusicDownloaderService()

__all__ = ["MusicDownloaderService", "music_downloader_service"]

