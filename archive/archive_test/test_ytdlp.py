#!/usr/bin/env python3
"""Test yt-dlp with URL to diagnose extraction issues"""

import sys
import yt_dlp
from loguru import logger

logger.remove()
logger.add(lambda msg: print(msg.rstrip()), format="{message}", level="INFO")

# Test URLs
test_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
]

print("=" * 60)
print("🧪 Testing yt-dlp with various URLs")
print("=" * 60)
print()

for url in test_urls:
    print(f"📌 Testing: {url[:50]}...")
    print()
    
    try:
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'skip_download': True,
            'extract_flat': False,
            'writesubtitles': False,
            'socket_timeout': 10,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("⏳ Extracting info...")
            info = ydl.extract_info(url, download=False)
            
            if info:
                print("✅ Success!")
                print(f"   Title: {info.get('title', 'Unknown')[:50]}")
                print(f"   Duration: {info.get('duration', 0)} seconds")
                print(f"   View count: {info.get('view_count', 0)}")
                print(f"   Formats: {len(info.get('formats', []))}")
            else:
                print("❌ No info returned")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()

print("=" * 60)
print("✅ Test complete")
print("=" * 60)
