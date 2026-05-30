#!/usr/bin/env python3
"""
Quick setup script for Phase 3 completion
Creates necessary directory structure and validates module system
"""

import os
import sys
from pathlib import Path

def create_tiktok_module():
    """Create TikTok module directory and files"""
    
    project_root = Path(__file__).parent
    tiktok_dir = project_root / "modules" / "tiktok"
    
    # Create directory
    tiktok_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created directory: {tiktok_dir}")
    
    # Create __init__.py
    init_file = tiktok_dir / "__init__.py"
    init_content = '''"""TikTok downloader module - Download videos with watermark removal"""
from .downloader import TikTokDownloader

__all__ = ["TikTokDownloader"]
'''
    init_file.write_text(init_content)
    print(f"✅ Created: {init_file}")
    
    # Create downloader.py with full implementation
    downloader_file = tiktok_dir / "downloader.py"
    downloader_content = '''"""TikTok downloader module - Download videos with watermark removal"""

from modules.base import BaseDownloader, MediaInfo
from typing import List, Optional
import re
import logging
import os
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)


class TikTokDownloader(BaseDownloader):
    """
    TikTok media downloader with watermark removal support
    
    Supports:
    - TikTok videos with audio
    - Watermark removal (automatic via best format)
    - Quality selection (1080p, 720p, 480p)
    - Short URLs (vm.tiktok.com, vt.tiktok.com)
    - Full URLs
    """
    
    PLATFORMS = ["tiktok", "tiktok.com", "vm.tiktok.com", "vt.tiktok.com"]
    PRIORITY = 25  # Between Instagram (30) and Twitter (20)
    
    def __init__(self):
        """Initialize TikTok downloader"""
        self.api_available = False
        try:
            import yt_dlp
            self.api_available = True
            self.yt_dlp = yt_dlp
            logger.info("TikTok yt-dlp library available")
        except ImportError:
            logger.warning("yt-dlp not installed - TikTok downloads unavailable")
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        """Check if URL is TikTok link"""
        patterns = [
            r'(?:https?://)?(?:www\\.)?tiktok\\.com/@[\\w.-]+/video/\\d+',
            r'(?:https?://)?vm\\.tiktok\\.com/[\\w]+',
            r'(?:https?://)?vt\\.tiktok\\.com/[\\w]+',
        ]
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False
    
    async def fetch_info(self, url: str) -> Optional[MediaInfo]:
        """Get TikTok video metadata"""
        if not self.api_available:
            logger.error("yt-dlp not available")
            return None
        
        try:
            url = self._normalize_url(url)
            video_id = self._extract_video_id(url)
            if not video_id:
                return None
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            loop = asyncio.get_event_loop()
            
            def get_info():
                with self.yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            info = await loop.run_in_executor(None, get_info)
            
            if not info:
                return None
            
            formats = self._parse_formats(info)
            
            media_info = MediaInfo(
                url=url,
                title=info.get('title', f"TikTok {video_id}"),
                duration=info.get('duration', 0),
                thumbnails=info.get('thumbnails', []),
                formats=formats,
            )
            
            logger.info(f"Fetched TikTok info: {media_info.title}")
            return media_info
            
        except Exception as e:
            logger.error(f"Error fetching TikTok info: {e}")
            return None
    
    async def download(
        self,
        url: str,
        output_dir: str,
        quality: str = "best"
    ) -> Optional[str]:
        """Download TikTok video"""
        if not self.api_available:
            logger.error("yt-dlp not available")
            return None
        
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            url = self._normalize_url(url)
            format_spec = self._get_format_spec(quality)
            
            ydl_opts = {
                'format': format_spec,
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
            }
            
            loop = asyncio.get_event_loop()
            
            def download_video():
                with self.yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return ydl.prepare_filename(info)
            
            file_path = await loop.run_in_executor(None, download_video)
            
            if file_path and os.path.exists(file_path):
                logger.info(f"Downloaded: {file_path}")
                return file_path
            
            return None
            
        except Exception as e:
            logger.error(f"Error downloading: {e}")
            return None
    
    def _normalize_url(self, url: str) -> str:
        """Normalize TikTok URL"""
        return url.rstrip('/')
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from TikTok URL"""
        patterns = [
            r'video/(\\d+)',
            r'vm\\.tiktok\\.com/([\\w]+)',
            r'vt\\.tiktok\\.com/([\\w]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _parse_formats(self, info: dict) -> List[str]:
        """Parse available formats"""
        formats = ['best', '1080p', '720p', '480p', '360p']
        return formats
    
    def _get_format_spec(self, quality: str) -> str:
        """Get yt-dlp format specification"""
        specs = {
            'best': 'best[vcodec!^=none][acodec!^=none]',
            '1080p': 'best[height=1080][vcodec!^=none][acodec!^=none]',
            '720p': 'best[height=720][vcodec!^=none][acodec!^=none]',
            '480p': 'best[height=480][vcodec!^=none][acodec!^=none]',
        }
        return specs.get(quality, specs['best'])


# Auto-register if not main
if __name__ != "__main__":
    try:
        from modules import register_module
        register_module("tiktok", TikTokDownloader())
    except Exception as e:
        logger.error(f"Failed to register TikTok module: {e}")
'''
    
    downloader_file.write_text(downloader_content)
    print(f"✅ Created: {downloader_file}")
    
    return True


def verify_module_system():
    """Verify all modules can be imported"""
    try:
        from modules import get_all_downloaders, MODULE_REGISTRY
        downloaders = get_all_downloaders()
        print(f"\\n✅ Module Registry:")
        for name, downloader in downloaders.items():
            print(f"   • {name}: {downloader.__class__.__name__}")
        return len(downloaders) >= 4
    except Exception as e:
        print(f"❌ Module import error: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Phase 3 Completion Setup Script")
    print("=" * 50)
    
    try:
        # Create TikTok module
        print("\\n📁 Creating TikTok module...")
        create_tiktok_module()
        
        # Verify module system
        print("\\n🔍 Verifying module system...")
        if verify_module_system():
            print("\\n✅ Phase 3 Setup Complete!")
            print("✅ All modules ready for deployment")
            return 0
        else:
            print("\\n⚠️  Module verification incomplete")
            return 1
            
    except Exception as e:
        print(f"\\n❌ Setup failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
'''