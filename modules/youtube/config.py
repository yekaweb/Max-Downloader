"""YouTube downloader configuration"""

YOUTUBE_CONFIG = {
    "ydl_opts": {
        # Video quality and format settings
        "format": "bestvideo+bestaudio/best",
        "quiet": False,
        "no_warnings": False,
        "prefer_insecure": False,
        # Networking
        "socket_timeout": 30,
        "extractor_args": {
            "youtube": {
                "lang": ["en"],  # Subtitles language
            }
        },
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
        "http_chunk_size": 1024 * 1024,  # 1MB chunks
        "buffer_size": 1024 * 20,  # 20KB buffer
        "ratelimit": None,  # No rate limiting
        # Retry settings
        "retries": 5,
        "fragment_retries": 5,
        "skip_unavailable_fragments": True,
        # Logging
        "quiet": True,
        "no_warnings": True,
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
