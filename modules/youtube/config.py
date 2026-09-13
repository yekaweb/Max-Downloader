"""YouTube downloader configuration"""

import os
from pathlib import Path

COOKIE_FILE = Path("/root/Max-Downloader/cookies.txt")

YOUTUBE_CONFIG = {
    "ydl_opts": {
        # Video quality and format settings
        "format": "bestvideo+bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "prefer_insecure": False,
        "cookiefile": str(COOKIE_FILE) if COOKIE_FILE.exists() else None,
        "js_runtimes": {"node": {}},
        "remote_components": ["ejs:github"],
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web_safari", "mweb", "ios"],
                "lang": ["en", "fa"],
            }
        },
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "http_headers": {
            "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
            "Sec-Fetch-Mode": "navigate",
        },
        # Networking
        "socket_timeout": 30,
        # Post-processing
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "prefixes": ["ffmpeg"],
                "prefixes_case": ["FFMPEG"],
                "args": ["-c:v", "copy", "-c:a", "aac"],
            }
        ],
        # Download settings
        "http_chunk_size": 1024 * 1024 * 5,  # 5MB chunks
        "buffer_size": 1024 * 64,            # 64KB buffer
        "ratelimit": None,
        # Retry settings
        "retries": 10,
        "fragment_retries": 10,
        "skip_unavailable_fragments": True,
    },
    # Download timeout in seconds
    "download_timeout": 3600,  # 1 hour
    # Maximum file size in bytes (0 = unlimited)
    "max_file_size": 0,
    # Enable subtitle downloading
    "download_subtitles": True,
    "subtitle_langs": ["all"],
    # Cache metadata for this duration (seconds)
    "cache_ttl": 3600,  # 1 hour
}

# Quality presets
QUALITY_PRESETS = {
    "best": "Best quality (up to 4K)",
    "good": "Good quality (1080p)",
    "medium": "Medium quality (720p)",
    "low": "Low quality (360p)",
    "audio": "Audio only (MP3)",
}

# Subtitle languages
SUBTITLE_LANGS = ["en", "fa", "ar", "ru", "zh"]

__all__ = ["YOUTUBE_CONFIG", "QUALITY_PRESETS", "SUBTITLE_LANGS"]
