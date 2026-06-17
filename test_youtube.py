import yt_dlp
import sys

opts = {
    'quiet': False,
    'cookiefile': '/app/cookies.txt',
    'extractor_args': {
        'youtube': {
            'player_client': ['web', 'android', 'ios'],
        }
    }
}

print("Testing YouTube extraction with your cookies.txt...")
try:
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info('https://www.youtube.com/watch?v=BaW_jenozKc', download=False)
        print(f"\n✅ SUCCESS! Found {len(info.get('formats', []))} formats.")
except Exception as e:
    print(f"\n❌ FAILED! YouTube rejected the request: {e}")
