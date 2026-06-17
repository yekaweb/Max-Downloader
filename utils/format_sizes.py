"""Utility for fetching exact file sizes from yt-dlp"""
import asyncio
from typing import Dict, Optional

import os

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

# Path to optional cookies file (place cookies.txt in project root on the server)
# Export from Chrome/Firefox using "Get cookies.txt LOCALLY" extension
COOKIES_FILE = "/app/cookies.txt"

def _build_ydl_opts(extra: dict = None) -> dict:
    """Build yt-dlp options with bot-detection bypass and optional cookies/OAuth2."""
    
    # 1. Professional Anti-Bot System: Persistent Cache
    cache_dir = '/app/cached_files/yt_dlp_cache'
    
    opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'socket_timeout': 30,
        'cachedir': cache_dir,
        # Rotate clients to mimic real users and bypass blocks
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'android', 'ios'],
            }
        },
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
        },
    }

    # Integrate proxy rotation if proxies.txt exists
    from utils.proxy_manager import get_random_proxy
    proxy = get_random_proxy()
    if proxy:
        opts['proxy'] = proxy

    # 2. Advanced Bypass: Prefer native OAuth2 token if generated
    oauth_token_path = os.path.join(cache_dir, 'youtube_oauth2_tokens.json')
    if os.path.isfile(oauth_token_path):
        opts['username'] = 'oauth2'
        opts['password'] = ''
    # 3. Fallback: Use cookies.txt if provided
    elif os.path.isfile(COOKIES_FILE):
        opts['cookiefile'] = COOKIES_FILE

    if extra:
        opts.update(extra)
    return opts

# Pre-built opts for metadata extraction only (no download)
_EXTRACT_YDL_OPTS = _build_ydl_opts({
    'skip_download': True,
    'extract_flat': False,
    'ignore_no_formats_error': True,  # Prevent crash if default format doesn't match
    'format': 'all',  # Fetch metadata for all formats to ensure robust extraction
})



async def get_exact_format_sizes(url: str) -> Dict:
    """
    Fetch exact file sizes for all available formats using yt-dlp.

    Returns on success:
    {
        "video_formats": {
            "4k":   {"size_mb": 2100.5 | None, "codec": "av01", "format_id": "..."},
            "1080p": {"size_mb": 850.3 | None,  "codec": "h264", "format_id": "..."},
            ...
        },
        "audio_formats": {
            "mp4a_129": {"size_mb": 3.3, "codec": "mp4a", "bitrate": 129, "format_id": "..."},
            ...
        },
        "codec_sizes": {
            "av01": {"size_mb": 229.2},
            "vp9":  {"size_mb": 8.9},
        },
        "title":    "Video Title",
        "duration": 213,
    }

    Returns on failure:
    {"error": "<error message>"}
    """
    if not yt_dlp:
        return {"error": "yt-dlp is not installed"}

    try:
        # Fix: use get_running_loop() — get_event_loop() is deprecated in Python 3.10+
        loop = asyncio.get_running_loop()

        # Run yt-dlp in executor to avoid blocking the async event loop
        info = await loop.run_in_executor(
            None,
            lambda: yt_dlp.YoutubeDL(_EXTRACT_YDL_OPTS).extract_info(url, download=False)
        )

        if not info:
            return {"error": "yt-dlp returned no info for this URL"}

        formats = info.get('formats', [])
        result = {
            "video_formats": {},
            "audio_formats": {},
            "codec_sizes": {},
            "title": info.get('title', 'Media'),
            "duration": info.get('duration', 0),
        }

        # ── Process VIDEO formats ─────────────────────────────────────────────
        video_by_height: Dict[int, list] = {}

        for fmt in formats:
            vcodec = fmt.get('vcodec')
            # Skip audio-only streams
            if not vcodec or vcodec == 'none':
                continue

            height = fmt.get('height') or 0
            if not height:
                continue  # Skip formats with unknown resolution

            # FIX Bug #3: do NOT gate on filesize — it is often None for DASH streams
            filesize = fmt.get('filesize') or fmt.get('filesize_approx') or 0

            codec_name = vcodec.split('.')[0]  # "avc1" → "h264" normalization below

            # Normalize codec names
            if codec_name.startswith('avc'):
                codec_name = 'h264'
            elif codec_name.startswith('av01'):
                codec_name = 'av1'
            elif codec_name.startswith('vp09') or codec_name.startswith('vp9'):
                codec_name = 'vp9'

            if height not in video_by_height:
                video_by_height[height] = []
            video_by_height[height].append({
                'filesize': filesize,
                'vcodec': codec_name,
                'format_id': fmt.get('format_id'),
                'ext': fmt.get('ext'),
            })

        # Map pixel heights to human-readable labels
        height_labels = {
            2160: '4k',
            1440: '1440p',
            1080: '1080p',
            720:  '720p',
            480:  '480p',
            360:  '360p',
            240:  '240p',
        }

        for height, label in height_labels.items():
            if height not in video_by_height:
                continue

            fmts = video_by_height[height]
            # Prefer entries with a known filesize for display
            fmts_with_size = [f for f in fmts if f['filesize'] > 0]
            best_fmt = (
                min(fmts_with_size, key=lambda x: x['filesize'])
                if fmts_with_size
                else fmts[0]
            )

            # FIX Bug #7: size_mb may be None — store None explicitly
            size_mb = round(best_fmt['filesize'] / (1024 * 1024), 1) if best_fmt['filesize'] else None

            result['video_formats'][label] = {
                'size_mb': size_mb,
                'codec': best_fmt['vcodec'],
                'format_id': best_fmt['format_id'],
                'ext': best_fmt['ext'],
            }

            # Track per-codec best size
            vcodec = best_fmt['vcodec']
            if vcodec not in result['codec_sizes'] and size_mb:
                result['codec_sizes'][vcodec] = {'size_mb': size_mb}

        # ── Process AUDIO-ONLY formats + Language/Dubbed tracks ──────────────
        # Language name map for common language codes
        _LANG_NAMES = {
            'en': 'English 🇺🇸', 'fa': 'فارسی 🇮🇷', 'ar': 'العربية 🇸🇦',
            'es': 'Español 🇪🇸', 'fr': 'Français 🇫🇷', 'de': 'Deutsch 🇩🇪',
            'ru': 'Русский 🇷🇺', 'zh': '中文 🇨🇳', 'ja': '日本語 🇯🇵',
            'ko': '한국어 🇰🇷', 'pt': 'Português 🇧🇷', 'tr': 'Türkçe 🇹🇷',
            'hi': 'हिन्दी 🇮🇳', 'it': 'Italiano 🇮🇹',
        }

        dubbed_tracks = {}  # {lang_code: {name, format_id, size_mb}}

        for fmt in formats:
            acodec = fmt.get('acodec')
            if not acodec or acodec == 'none':
                continue
            if fmt.get('vcodec') not in (None, 'none'):
                continue  # Skip muxed streams

            filesize = fmt.get('filesize') or fmt.get('filesize_approx') or 0
            lang = fmt.get('language') or ''
            lang_code = lang.split('-')[0].lower() if lang else ''  # 'en-US' → 'en'

            # Phase 5.1: collect dubbed/alternative audio tracks by language
            if lang_code and lang_code not in dubbed_tracks:
                size_mb = round(filesize / (1024 * 1024), 1) if filesize else None
                dubbed_tracks[lang_code] = {
                    'name': _LANG_NAMES.get(lang_code, lang_code.upper()),
                    'format_id': fmt.get('format_id'),
                    'size_mb': size_mb,
                }

            if not filesize:
                continue

            codec_name = acodec.split('.')[0]
            abr = fmt.get('abr') or 0
            size_mb = round(filesize / (1024 * 1024), 1)
            label = f'{codec_name}_{int(abr)}'

            result['audio_formats'][label] = {
                'size_mb': size_mb,
                'codec': codec_name,
                'bitrate': int(abr),
                'format_id': fmt.get('format_id'),
            }

        # Only include dubbed_tracks if more than one language track exists
        if len(dubbed_tracks) > 1:
            result['dubbed_tracks'] = dubbed_tracks

        return result


    except Exception as e:
        return {"error": str(e)}


def format_size_mb(size_mb: Optional[float]) -> str:
    """Format MB size nicely. Handles None gracefully."""
    if size_mb is None:
        return "نامشخص"
    if size_mb > 1024:
        return f"{size_mb / 1024:.1f} GB"
    return f"{size_mb:.1f} MB"


__all__ = ["get_exact_format_sizes", "format_size_mb"]
