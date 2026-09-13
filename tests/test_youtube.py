import pytest
import yt_dlp
from pathlib import Path

COOKIE_FILE = Path("/root/Max-Downloader/cookies.txt")

def test_youtube_extraction():
    opts = {
        'quiet': True,
        'no_warnings': True,
        'cookiefile': str(COOKIE_FILE) if COOKIE_FILE.exists() else None,
        'js_runtimes': {'node': {}},
        'remote_components': ['ejs:github'],
        'extractor_args': {
            'youtube': {
                'player_client': ['all'],
                'lang': ['en', 'fa'],
            }
        },
        'skip_download': True,
    }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info('https://www.youtube.com/watch?v=dQw4w9WgXcQ', download=False)
        assert info is not None
        assert 'formats' in info
        assert len(info['formats']) > 0

