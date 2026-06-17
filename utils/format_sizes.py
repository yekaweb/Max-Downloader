"""Utility for fetching exact file sizes from yt-dlp"""
import asyncio
from typing import Dict, Optional

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

# Shared ydl_opts for metadata extraction (bot-detection bypass)
_EXTRACT_YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'extract_flat': False,
    'noplaylist': True,
    'socket_timeout': 30,
    # Use Android client to bypass datacenter IP bot-detection
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web'],
        }
    },
    'http_headers': {
        'User-Agent': (
            'Mozilla/5.0 (Linux; Android 11; Pixel 5) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/90.0.4430.91 Mobile Safari/537.36'
        ),
    },
}


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

        # ── Process AUDIO-ONLY formats ────────────────────────────────────────
        for fmt in formats:
            acodec = fmt.get('acodec')
            if not acodec or acodec == 'none':
                continue
            if fmt.get('vcodec') not in (None, 'none'):
                continue  # Skip muxed streams

            filesize = fmt.get('filesize') or fmt.get('filesize_approx') or 0
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
