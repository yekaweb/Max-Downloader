"""
Instagram Service for DLBot.
Handles Instagram session management, cookies injection, and media downloading via yt-dlp & instagrapi.
"""

import os
import re
import json
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, Callable

import yt_dlp
from utils.proxy_manager import get_random_proxy

logger = logging.getLogger(__name__)

BASE_DIR = Path("/root/Max-Downloader")
COOKIE_FILE = BASE_DIR / "cookies.txt"
SESSION_FILE = BASE_DIR / "cached_files" / "instagram_session.json"

INSTAGRAM_REGEX = re.compile(
    r"(https?://)?(www\.)?(instagram\.com|insta\.io)/(p|reel|tv|stories|reels)/[A-Za-z0-9\-_]+"
)


class InstagramService:
    """
    Unified Instagram Service supporting:
    - Session ID & Cookie persistence
    - Dual-engine extraction (yt-dlp + instagrapi)
    - Admin session management
    """

    def __init__(self):
        self._cached_session_id: Optional[str] = None
        self._load_persisted_session()

    @classmethod
    def is_instagram_url(cls, url: str) -> bool:
        """Check if a given URL is an Instagram link."""
        return bool(INSTAGRAM_REGEX.search(url or ""))

    def _load_persisted_session(self):
        """Load session ID from session file or cookies.txt if present."""
        try:
            if SESSION_FILE.exists():
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._cached_session_id = data.get("sessionid")
            elif COOKIE_FILE.exists():
                with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        if "instagram.com" in line and "sessionid" in line:
                            parts = line.strip().split()
                            if len(parts) >= 7:
                                self._cached_session_id = parts[6]
                                break
        except Exception as e:
            logger.warning(f"[InstagramService] Failed to load session: {e}")

    def has_active_session(self) -> bool:
        """Check if a session ID is configured."""
        return bool(self._cached_session_id)

    def set_session_id(self, session_id: str, ds_user_id: str = "") -> bool:
        """
        Save and activate an Instagram session ID.
        Updates instagram_session.json and injects Netscape cookies into cookies.txt.
        """
        session_id = (session_id or "").strip()
        if not session_id:
            return False

        self._cached_session_id = session_id

        # 1. Save to JSON session file
        try:
            SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump({"sessionid": session_id, "ds_user_id": ds_user_id}, f, indent=2)
        except Exception as e:
            logger.error(f"[InstagramService] Error writing session file: {e}")

        # 2. Inject / Update cookies.txt
        try:
            existing_lines = []
            if COOKIE_FILE.exists():
                with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                    existing_lines = [l for l in f if "instagram.com" not in l]

            # Netscape HTTP Cookie File format
            ig_cookies = [
                f".instagram.com\tTRUE\t/\tTRUE\t1899999999\tsessionid\t{session_id}\n",
            ]
            if ds_user_id:
                ig_cookies.append(
                    f".instagram.com\tTRUE\t/\tTRUE\t1899999999\tds_user_id\t{ds_user_id}\n"
                )

            with open(COOKIE_FILE, "w", encoding="utf-8") as f:
                if not existing_lines or not existing_lines[0].startswith("# Netscape"):
                    f.write("# Netscape HTTP Cookie File\n")
                for line in existing_lines:
                    if line.strip():
                        f.write(line.rstrip() + "\n")
                for line in ig_cookies:
                    f.write(line)

            logger.info("[InstagramService] Successfully updated cookies.txt with Instagram session.")
            return True
        except Exception as e:
            logger.error(f"[InstagramService] Error updating cookies.txt: {e}")
            return False

    async def get_media_info(self, url: str) -> Dict[str, Any]:
        """
        Fetch Instagram media information.
        Returns metadata dict on success or {"error": "..."} on failure.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._extract_info_sync, url)

    def _extract_info_sync(self, url: str) -> Dict[str, Any]:
        """Synchronous info extraction with yt-dlp & fallback."""
        clean_url = url.split("?")[0].rstrip("/")
        if not clean_url.startswith("http"):
            clean_url = f"https://{clean_url}"

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "cookiefile": str(COOKIE_FILE) if COOKIE_FILE.exists() else None,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
            },
            "socket_timeout": 20,
        }
        proxy = get_random_proxy()
        if proxy:
            ydl_opts["proxy"] = proxy

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                if not info:
                    return {"error": "اطلاعاتی برای این لینک یافت نشد."}

                duration = info.get("duration", 0)
                title = info.get("title") or f"Instagram Reel ({info.get('id', '')})"
                filesize = info.get("filesize") or info.get("filesize_approx") or 0
                size_mb = round(filesize / (1024 * 1024), 1) if filesize else 15.0

                return {
                    "title": title,
                    "duration": duration,
                    "platform": "instagram",
                    "video_formats": {
                        "original": {"size_mb": size_mb, "codec": "h264", "format_id": "best"},
                    },
                    "audio_formats": {
                        "mp3": {"size_mb": round((duration * 16000) / (1024 * 1024), 1) if duration else 3.5, "codec": "mp3", "bitrate": 128},
                    },
                    "codec_sizes": {"h264": {"size_mb": size_mb}},
                    "url": clean_url,
                }
        except yt_dlp.utils.DownloadError as e:
            msg = str(e).lower()
            if "login required" in msg or "rate-limit" in msg or "not available" in msg:
                # Try instagrapi fallback if session exists
                if self.has_active_session():
                    try:
                        from instagrapi import Client
                        cl = Client()
                        cl.login_by_sessionid(self._cached_session_id)
                        pk = cl.media_pk_from_url(clean_url)
                        m_info = cl.media_info(pk)
                        return {
                            "title": m_info.caption_text[:60] if m_info.caption_text else f"Instagram Media {pk}",
                            "duration": getattr(m_info, "video_duration", 0) or 0,
                            "platform": "instagram",
                            "video_formats": {"original": {"size_mb": 15.0, "codec": "h264", "format_id": "best"}},
                            "audio_formats": {"mp3": {"size_mb": 3.0, "codec": "mp3", "bitrate": 128}},
                            "codec_sizes": {"h264": {"size_mb": 15.0}},
                            "url": clean_url,
                        }
                    except Exception as ig_err:
                        logger.warning(f"[InstagramService] Instagrapi fallback failed: {ig_err}")

                return {
                    "error": "LOGIN_REQUIRED",
                    "details": "اینستاگرام به دلیل محدودیت آی‌پی سرور نیاز به تنظیم کوکی دارد.",
                }
            return {"error": str(e)[:200]}
        except Exception as exc:
            return {"error": str(exc)[:200]}


instagram_service = InstagramService()

__all__ = ["InstagramService", "instagram_service"]
