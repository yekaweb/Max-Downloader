"""Utility for fetching exact file sizes from yt-dlp"""
import asyncio
from typing import Dict, List, Optional, Tuple
try:
    import yt_dlp
except ImportError:
    yt_dlp = None


async def get_exact_format_sizes(url: str) -> Dict[str, Dict]:
    """
    Fetch exact file sizes for all available formats using yt-dlp.
    
    Returns:
    {
        "video_formats": {
            "4k": {"size_mb": 2100.5, "codec": "h264", "format_id": "..."},
            "1080p": {"size_mb": 850.3, "codec": "h264", "format_id": "..."},
            ...
        },
        "audio_formats": {
            "mp3_320": {"size_mb": 25.3, "codec": "mp3", "format_id": "..."},
            ...
        },
        "codec_sizes": {
            "h264": {"size_mb": 850.3},
            "av1": {"size_mb": 520.5},
            "vp9": {"size_mb": 610.2},
        }
    }
    """
    if not yt_dlp:
        return {}
    
    try:
        # Extract info without downloading
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': False,
        }
        
        loop = asyncio.get_event_loop()
        
        # Run yt-dlp in executor to avoid blocking
        info = await loop.run_in_executor(
            None,
            lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=False)
        )
        
        if not info:
            return {}
        
        formats = info.get('formats', [])
        result = {
            "video_formats": {},
            "audio_formats": {},
            "codec_sizes": {},
            "title": info.get('title', 'Media'),
            "duration": info.get('duration', 0),
        }
        
        # Process video formats
        video_by_height = {}
        for fmt in formats:
            if fmt.get('vcodec') != 'none' and fmt.get('vcodec'):  # Has video
                height = fmt.get('height', 0)
                filesize = fmt.get('filesize') or fmt.get('filesize_approx', 0)
                
                if height and filesize:
                    if height not in video_by_height:
                        video_by_height[height] = []
                    
                    vcodec = fmt.get('vcodec', 'unknown').split('.')[0]  # h264, av1, vp9
                    video_by_height[height].append({
                        'filesize': filesize,
                        'vcodec': vcodec,
                        'format_id': fmt.get('format_id'),
                        'ext': fmt.get('ext'),
                    })
        
        # Build video formats result
        height_labels = {
            2160: '4k',
            1440: '1440p',
            1080: '1080p',
            720: '720p',
            480: '480p',
            360: '360p',
            240: '240p',
        }
        
        for height, label in height_labels.items():
            if height in video_by_height:
                # Get the smallest filesize for this height
                best_fmt = min(video_by_height[height], key=lambda x: x['filesize'])
                size_mb = best_fmt['filesize'] / (1024 * 1024)
                vcodec = best_fmt['vcodec']
                
                result['video_formats'][label] = {
                    'size_mb': round(size_mb, 1),
                    'codec': vcodec,
                    'format_id': best_fmt['format_id'],
                    'ext': best_fmt['ext'],
                }
                
                # Track codec sizes
                if vcodec not in result['codec_sizes']:
                    result['codec_sizes'][vcodec] = {'size_mb': round(size_mb, 1)}
        
        # Process audio formats
        for fmt in formats:
            if fmt.get('acodec') != 'none' and fmt.get('acodec') and fmt.get('vcodec') == 'none':
                filesize = fmt.get('filesize') or fmt.get('filesize_approx', 0)
                acodec = fmt.get('acodec', 'unknown').split('.')[0]
                abr = fmt.get('abr', 128)
                
                if filesize and acodec:
                    size_mb = filesize / (1024 * 1024)
                    label = f'{acodec}_{int(abr)}'
                    
                    result['audio_formats'][label] = {
                        'size_mb': round(size_mb, 1),
                        'codec': acodec,
                        'bitrate': int(abr),
                        'format_id': fmt.get('format_id'),
                    }
        
        return result
    
    except Exception as e:
        print(f"Error fetching format sizes: {e}")
        return {"error": str(e)}


def format_size_mb(size_mb: float) -> str:
    """Format MB size nicely"""
    if size_mb > 1024:
        return f"{size_mb / 1024:.1f} GB"
    return f"{size_mb:.1f} MB"


__all__ = ["get_exact_format_sizes", "format_size_mb"]
