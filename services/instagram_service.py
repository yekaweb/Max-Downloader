"""
Instagram Service for DLBot.
Next-Generation 4-Tier Waterfall Engine for Zero-Login, Instant Instagram Downloading:
  - Tier 1: Direct Embed / Public HTML Scraper (Zero Auth, ~300ms, direct CDN URLs)
  - Tier 2: Cobalt Multi-Instance API Engine (Reels, Videos, Carousel Pickers)
  - Tier 3: Rapid Multi-Source Scraper Resolver
  - Tier 4: Native yt-dlp & Instagrapi Session Fallback
"""

import os
import re
import html
import json
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Callable

import aiohttp
import yt_dlp
from utils.proxy_manager import get_random_proxy
from services.cobalt_service import cobalt_service

logger = logging.getLogger(__name__)

BASE_DIR = Path("/root/Max-Downloader")
COOKIE_FILE = BASE_DIR / "cookies.txt"
SESSION_FILE = BASE_DIR / "cached_files" / "instagram_session.json"

INSTAGRAM_REGEX = re.compile(
    r"(https?://)?(www\.)?(instagram\.com|insta\.io)/(p|reel|tv|stories|reels)/([A-Za-z0-9\-_]+)"
)


class InstagramService:
    """
    Unified Next-Gen Instagram Service supporting:
    - Instant Zero-Login direct CDN stream extraction (Embed + Cobalt + Scraper)
    - Single video/reel, single photo, and multi-slide Carousel (MediaGroup)
    - Session ID & Cookie persistence for restricted/private profiles
    - Admin session management
    """

    def __init__(self):
        self._cached_session_id: Optional[str] = None
        self._load_persisted_session()

    @classmethod
    def is_instagram_url(cls, url: str) -> bool:
        """Check if a given URL is an Instagram link."""
        return bool(INSTAGRAM_REGEX.search(url or ""))

    @classmethod
    def extract_shortcode(cls, url: str) -> Optional[str]:
        """Extract post or reel shortcode from an Instagram URL."""
        match = INSTAGRAM_REGEX.search(url or "")
        if match:
            return match.group(5)
        return None

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

    def login_with_credentials(
        self, username: str, password: str, verification_code: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Authenticate with Instagram using username & password via instagrapi.
        Extracts and persists sessionid automatically.
        """
        try:
            from instagrapi import Client
            from instagrapi.exceptions import (
                TwoFactorRequired,
                BadPassword,
                PleaseWaitFewMinutes,
                ChallengeRequired,
            )

            cl = Client()
            proxy = get_random_proxy()
            if proxy:
                cl.set_proxy(proxy)

            logged_in = False
            if verification_code:
                logged_in = cl.login(username, password, verification_code=verification_code)
            else:
                logged_in = cl.login(username, password)

            if logged_in or cl.sessionid:
                session_id = cl.sessionid
                user_id = str(cl.user_id) if getattr(cl, "user_id", None) else ""
                self.set_session_id(session_id, user_id)
                return True, f"✅ با موفقیت به اکانت {username} متصل شد و سشن فعال گردید."
            return False, "❌ لاگین انجام نشد. لطفاً مشخصات را بررسی کنید."
        except TwoFactorRequired:
            return False, "⚠️ اکانت دارای تایید دو مرحله‌ای (2FA) است. لطفاً کد را نیز ارسال کنید:\n<code>/ig_login username password code</code>"
        except BadPassword:
            return False, "❌ نام کاربری یا رمز عبور اینستاگرام اشتباه است."
        except PleaseWaitFewMinutes:
            return False, "⚠️ اینستاگرام موقتاً محدود کرده است. لطفاً چند دقیقه دیگر امتحان کنید."
        except ChallengeRequired:
            return False, "⚠️ اینستاگرام درخواست تایید هویت (Challenge) داده است. لطفاً یک‌بار در مرورگر وارد اکانت شوید."
        except Exception as e:
            logger.error(f"[InstagramService] Login error: {e}")
            return False, f"❌ خطا در لاگین: {str(e)[:150]}"

    # =========================================================================
    # NEXT-GEN WATERFALL RESOLUTION ENGINES (ZERO AUTH & ULTRA-FAST)
    # =========================================================================

    async def resolve_media(self, url: str) -> Dict[str, Any]:
        """
        Master Waterfall Resolution Entrypoint:
        Tries Tier 1 (Embed) -> Tier 2 (Cobalt) -> Tier 3 (Scraper APIs) -> Tier 4 (yt-dlp/Instagrapi).
        Returns structured dict with media items, direct URLs, caption, and engine info.
        """
        clean_url = url.split("?")[0].rstrip("/")
        if not clean_url.startswith("http"):
            clean_url = f"https://{clean_url}"

        shortcode = self.extract_shortcode(clean_url) or "media"

        # ----------------------------------------------------
        # TIER 1: Direct Embed Scraper (Zero Auth, ~300ms)
        # ----------------------------------------------------
        try:
            logger.info(f"[InstagramService] Attempting Tier 1 (Direct Embed) for {clean_url}")
            res_embed = await self._resolve_via_embed(clean_url, shortcode)
            if res_embed and res_embed.get("success"):
                logger.info(f"[InstagramService] Tier 1 succeeded for {shortcode}")
                return res_embed
        except Exception as e:
            logger.debug(f"[InstagramService] Tier 1 failed: {e}")

        # ----------------------------------------------------
        # TIER 2: Cobalt Multi-Instance Engine (~800ms)
        # ----------------------------------------------------
        try:
            logger.info(f"[InstagramService] Attempting Tier 2 (Cobalt API) for {clean_url}")
            res_cobalt = await self._resolve_via_cobalt(clean_url, shortcode)
            if res_cobalt and res_cobalt.get("success"):
                logger.info(f"[InstagramService] Tier 2 succeeded for {shortcode}")
                return res_cobalt
        except Exception as e:
            logger.debug(f"[InstagramService] Tier 2 failed: {e}")

        # ----------------------------------------------------
        # TIER 3: Rapid Public Scraper APIs (~1.2s)
        # ----------------------------------------------------
        try:
            logger.info(f"[InstagramService] Attempting Tier 3 (Public Scrapers) for {clean_url}")
            res_scraper = await self._resolve_via_public_scrapers(clean_url, shortcode)
            if res_scraper and res_scraper.get("success"):
                logger.info(f"[InstagramService] Tier 3 succeeded for {shortcode}")
                return res_scraper
        except Exception as e:
            logger.debug(f"[InstagramService] Tier 3 failed: {e}")

        # ----------------------------------------------------
        # TIER 4: Fallback to yt-dlp / Instagrapi
        # ----------------------------------------------------
        try:
            logger.info(f"[InstagramService] Attempting Tier 4 (yt-dlp/Instagrapi) for {clean_url}")
            res_native = await self._resolve_via_ytdlp_or_instagrapi(clean_url, shortcode)
            if res_native and res_native.get("success"):
                logger.info(f"[InstagramService] Tier 4 succeeded for {shortcode}")
                return res_native
        except Exception as e:
            logger.error(f"[InstagramService] Tier 4 failed: {e}")

        return {
            "success": False,
            "error": "LOGIN_REQUIRED" if not self.has_active_session() else "FAILED_TO_RESOLVE",
            "message": "متاسفانه دریافت محتوا امکان‌پذیر نشد. در صورت خصوصی بودن پیج، نیاز به اتصال اکانت در ربات می‌باشد.",
        }

    async def _resolve_via_embed(self, url: str, shortcode: str) -> Optional[Dict[str, Any]]:
        """
        Tier 1: Scrape Instagram's public embed page without authentication.
        """
        embed_url = f"https://www.instagram.com/p/{shortcode}/embed/captioned/"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(embed_url, headers=headers) as resp:
                if resp.status != 200:
                    return None
                text = await resp.text()

        # 1. Search for direct video URL in embed page
        video_urls = []
        # Pattern 1: JSON video_url
        v_matches = re.findall(r'"video_url":"([^"]+)"', text)
        for vm in v_matches:
            clean_v = html.unescape(vm.replace("\\u0026", "&").replace("\\/", "/"))
            if clean_v.startswith("http") and clean_v not in video_urls:
                video_urls.append(clean_v)

        # Pattern 2: data-video-url or src
        if not video_urls:
            v_data = re.findall(r'data-video-url="([^"]+)"', text)
            for vd in v_data:
                clean_v = html.unescape(vd.replace("&amp;", "&"))
                if clean_v.startswith("http") and clean_v not in video_urls:
                    video_urls.append(clean_v)

        # 2. Search for images if no video or as carousel fallback
        photo_urls = []
        p_matches = re.findall(r'"display_url":"([^"]+)"', text)
        for pm in p_matches:
            clean_p = html.unescape(pm.replace("\\u0026", "&").replace("\\/", "/"))
            if clean_p.startswith("http") and clean_p not in photo_urls:
                photo_urls.append(clean_p)

        if not photo_urls:
            p_src = re.findall(r'class="EmbeddedMediaImage"[^>]*src="([^"]+)"', text)
            for ps in p_src:
                clean_p = html.unescape(ps.replace("&amp;", "&"))
                if clean_p.startswith("http") and clean_p not in photo_urls:
                    photo_urls.append(clean_p)

        # 3. Extract Caption
        caption = ""
        c_match = re.search(r'<div class="Caption"[^>]*>(.*?)</div>', text, re.DOTALL)
        if c_match:
            raw_caption = re.sub(r"<[^>]+>", "", c_match.group(1))
            caption = html.unescape(raw_caption).strip()

        if video_urls:
            items = [{"type": "video", "url": v, "thumbnail": photo_urls[0] if photo_urls else None} for v in video_urls]
            return {
                "success": True,
                "platform": "instagram",
                "shortcode": shortcode,
                "title": f"Instagram Reel ({shortcode})",
                "caption": caption,
                "is_album": len(items) > 1,
                "items": items,
                "engine": "Direct Embed (Zero-Auth)",
            }
        elif photo_urls:
            items = [{"type": "photo", "url": p} for p in photo_urls]
            return {
                "success": True,
                "platform": "instagram",
                "shortcode": shortcode,
                "title": f"Instagram Post ({shortcode})",
                "caption": caption,
                "is_album": len(items) > 1,
                "items": items,
                "engine": "Direct Embed (Zero-Auth)",
            }

        return None

    async def _resolve_via_cobalt(self, url: str, shortcode: str) -> Optional[Dict[str, Any]]:
        """
        Tier 2: Use Cobalt API with carousel/picker support.
        """
        payload = {
            "url": url,
            "videoQuality": "1080",
            "downloadMode": "auto",
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DLBot-Titan/2.0",
        }

        instances = [
            "https://api.cobalt.tools",
            "https://cobalt-api.kwiatekm.pl",
            "https://api.server.im",
            "https://cobalt.xy2.dev",
            "https://co.wuk.sh",
        ]

        timeout = aiohttp.ClientTimeout(total=8)
        for instance in instances:
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(f"{instance.rstrip('/')}/", json=payload, headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            status = data.get("status")
                            if status in ["stream", "redirect", "tunnel"]:
                                media_url = data.get("url")
                                if media_url:
                                    return {
                                        "success": True,
                                        "platform": "instagram",
                                        "shortcode": shortcode,
                                        "title": data.get("filename", f"Instagram ({shortcode})"),
                                        "caption": "",
                                        "is_album": False,
                                        "items": [{"type": "video", "url": media_url}],
                                        "engine": f"Cobalt API ({instance})",
                                    }
                            elif status == "picker":
                                picker_items = data.get("picker", [])
                                if picker_items:
                                    items = []
                                    for pi in picker_items:
                                        m_type = "photo" if pi.get("type") == "photo" else "video"
                                        items.append({"type": m_type, "url": pi.get("url"), "thumbnail": pi.get("thumb")})
                                    return {
                                        "success": True,
                                        "platform": "instagram",
                                        "shortcode": shortcode,
                                        "title": f"Instagram Album ({shortcode})",
                                        "caption": "",
                                        "is_album": len(items) > 1,
                                        "items": items,
                                        "engine": f"Cobalt API ({instance})",
                                    }
            except Exception as e:
                logger.debug(f"[Cobalt] Instance {instance} error: {e}")
                continue

        return None

    async def _resolve_via_public_scrapers(self, url: str, shortcode: str) -> Optional[Dict[str, Any]]:
        """
        Tier 3: Query public scraper API mirrors (ddinstagram / save / rapid scrapers).
        """
        # DDInstagram Web Extractor
        dd_url = f"https://ddinstagram.com/videos/{shortcode}/1"
        timeout = aiohttp.ClientTimeout(total=6)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.head(dd_url, allow_redirects=True) as resp:
                    if resp.status == 200 and "video" in resp.headers.get("Content-Type", ""):
                        final_url = str(resp.url)
                        return {
                            "success": True,
                            "platform": "instagram",
                            "shortcode": shortcode,
                            "title": f"Instagram Reel ({shortcode})",
                            "caption": "",
                            "is_album": False,
                            "items": [{"type": "video", "url": final_url}],
                            "engine": "DDInstagram Extractor",
                        }
        except Exception as e:
            logger.debug(f"[PublicScrapers] DDInstagram head check failed: {e}")

        return None

    async def _resolve_via_ytdlp_or_instagrapi(self, url: str, shortcode: str) -> Optional[Dict[str, Any]]:
        """
        Tier 4: Native yt-dlp extraction with cookie / instagrapi fallback.
        """
        loop = asyncio.get_running_loop()

        def _sync_ytdlp():
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "cookiefile": str(COOKIE_FILE) if COOKIE_FILE.exists() else None,
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
                },
                "socket_timeout": 15,
            }
            proxy = get_random_proxy()
            if proxy:
                ydl_opts["proxy"] = proxy

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    return None

                entries = info.get("entries")
                if entries:
                    items = []
                    for entry in entries:
                        e_url = entry.get("url")
                        if e_url:
                            m_type = "video" if entry.get("vcodec") != "none" else "photo"
                            items.append({"type": m_type, "url": e_url, "thumbnail": entry.get("thumbnail")})
                    if items:
                        return {
                            "success": True,
                            "platform": "instagram",
                            "shortcode": shortcode,
                            "title": info.get("title", f"Instagram Media ({shortcode})"),
                            "caption": info.get("description", ""),
                            "is_album": len(items) > 1,
                            "items": items,
                            "engine": "yt-dlp Session Engine",
                        }

                direct_url = info.get("url")
                if direct_url:
                    m_type = "video" if info.get("vcodec") != "none" else "photo"
                    return {
                        "success": True,
                        "platform": "instagram",
                        "shortcode": shortcode,
                        "title": info.get("title", f"Instagram Media ({shortcode})"),
                        "caption": info.get("description", ""),
                        "is_album": False,
                        "items": [{"type": m_type, "url": direct_url, "thumbnail": info.get("thumbnail")}],
                        "engine": "yt-dlp Session Engine",
                    }
            return None

        # Try yt-dlp first
        try:
            res = await loop.run_in_executor(None, _sync_ytdlp)
            if res:
                return res
        except Exception as e:
            logger.debug(f"[yt-dlp] Sync extraction failed: {e}")

        # Try instagrapi if session is configured
        if self.has_active_session():
            def _sync_instagrapi():
                from instagrapi import Client
                cl = Client()
                cl.login_by_sessionid(self._cached_session_id)
                pk = cl.media_pk_from_url(url)
                m_info = cl.media_info(pk)
                
                # Check media type: 1=Photo, 2=Video/Reel, 8=Album
                if m_info.media_type == 8:  # Album
                    items = []
                    for resource in m_info.resources:
                        if resource.media_type == 2 and resource.video_url:
                            items.append({"type": "video", "url": str(resource.video_url)})
                        elif resource.thumbnail_url:
                            items.append({"type": "photo", "url": str(resource.thumbnail_url)})
                    return {
                        "success": True,
                        "platform": "instagram",
                        "shortcode": shortcode,
                        "title": f"Instagram Album ({shortcode})",
                        "caption": m_info.caption_text or "",
                        "is_album": len(items) > 1,
                        "items": items,
                        "engine": "Instagrapi Authenticated Engine",
                    }
                elif m_info.media_type == 2 and getattr(m_info, "video_url", None):
                    return {
                        "success": True,
                        "platform": "instagram",
                        "shortcode": shortcode,
                        "title": f"Instagram Reel ({shortcode})",
                        "caption": m_info.caption_text or "",
                        "is_album": False,
                        "items": [{"type": "video", "url": str(m_info.video_url)}],
                        "engine": "Instagrapi Authenticated Engine",
                    }
                elif getattr(m_info, "thumbnail_url", None):
                    return {
                        "success": True,
                        "platform": "instagram",
                        "shortcode": shortcode,
                        "title": f"Instagram Photo ({shortcode})",
                        "caption": m_info.caption_text or "",
                        "is_album": False,
                        "items": [{"type": "photo", "url": str(m_info.thumbnail_url)}],
                        "engine": "Instagrapi Authenticated Engine",
                    }
                return None

            try:
                res_ig = await loop.run_in_executor(None, _sync_instagrapi)
                if res_ig:
                    return res_ig
            except Exception as ig_err:
                logger.warning(f"[Instagrapi] Session extraction failed: {ig_err}")

        return None

    async def get_media_info(self, url: str) -> Dict[str, Any]:
        """Backward compatibility helper for get_media_info."""
        res = await self.resolve_media(url)
        if res.get("success"):
            items = res.get("items", [])
            first_item = items[0] if items else {}
            return {
                "title": res.get("title", "Instagram Media"),
                "duration": 0,
                "platform": "instagram",
                "video_formats": {
                    "original": {"size_mb": 15.0, "codec": "h264", "format_id": "best"},
                },
                "audio_formats": {
                    "mp3": {"size_mb": 3.5, "codec": "mp3", "bitrate": 128},
                },
                "codec_sizes": {"h264": {"size_mb": 15.0}},
                "url": url,
                "resolved_data": res,
            }
        return {"error": res.get("error", "FAILED_TO_RESOLVE")}


instagram_service = InstagramService()

__all__ = ["InstagramService", "instagram_service"]

