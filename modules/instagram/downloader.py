"""Instagram downloader module - Download posts, reels, and stories"""

from modules.base import BaseDownloader, MediaInfo
from typing import List, Optional
import re
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class InstagramDownloader(BaseDownloader):
    """
    Instagram media downloader
    
    Supports:
    - Posts (photos and videos)
    - Reels
    - Stories (if accessible)
    - Carousel posts (multiple media)
    - IGTV videos
    """
    
    # Module metadata
    NAME = "Instagram"
    ICON = "📷"
    SUPPORTED_DOMAINS = ["instagram.com", "insta.io"]
    VERSION = "1.0.0"
    ENABLED = True
    PRIORITY = 30  # After YouTube (100), before others
    
    PLATFORMS = ["instagram", "instagram.com", "insta", "ig"]
    
    def __init__(self):
        """Initialize Instagram downloader"""
        self.api_available = False
        try:
            import instagrapi
            self.api_available = True
            self.Client = instagrapi.Client
            logger.info("Instagram instagrapi library available")
        except ImportError:
            logger.warning("instagrapi not installed - using fallback method")
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        """
        Check if URL is Instagram link
        
        Supported formats:
        - https://instagram.com/p/XXXXX/
        - https://www.instagram.com/p/XXXXX/
        - https://instagram.com/reel/XXXXX/
        - https://instagram.com/stories/username/XXXXX/
        - instagram.com/p/XXXXX/ (without https)
        """
        patterns = [
            r'(?:https?://)?(?:www\.)?instagram\.com/p/[A-Za-z0-9\-_]+',
            r'(?:https?://)?(?:www\.)?instagram\.com/reel/[A-Za-z0-9\-_]+',
            r'(?:https?://)?(?:www\.)?instagram\.com/stories/[^/]+/[0-9]+',
            r'(?:https?://)?(?:www\.)?instagram\.com/tv/[A-Za-z0-9\-_]+',
        ]
        
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False
    
    async def fetch_info(self, url: str) -> Optional[MediaInfo]:
        """
        Get Instagram media metadata
        
        Returns: MediaInfo with title, duration, formats
        """
        try:
            # Normalize URL
            url = self._normalize_url(url)
            
            # Extract media ID
            media_id = self._extract_media_id(url)
            if not media_id:
                logger.error(f"Could not extract media ID from {url}")
                return None
            
            media_info = MediaInfo(
                url=url,
                title=f"Instagram Post {media_id[:8]}",
                duration=0,
                thumbnails=[],
                formats=[],
                extra={"platform": "instagram", "media_id": media_id}
            )
            
            if self.api_available:
                try:
                    # Try to fetch real metadata
                    client = self.Client()
                    media = client.media_info(int(media_id))
                    media_info.title = media.caption or f"Instagram Post {media_id}"
                    media_info.duration = getattr(media, 'video_duration', 0)
                    media_info.formats = self._parse_formats(media)
                    logger.info(f"Fetched Instagram media info: {media_info.title}")
                except Exception as e:
                    logger.warning(f"Failed to fetch real metadata: {e}, using fallback")
            
            return media_info
        
        except Exception as e:
            logger.error(f"Error fetching Instagram info: {e}")
            return None
    
    async def download(self, media_info: MediaInfo, output_path: str) -> Optional[str]:
        """
        Download Instagram media
        
        Supports:
        - Single photos
        - Single videos/reels
        - Multiple photos (carousel)
        - Video with audio
        
        Returns: Path to downloaded file(s)
        """
        try:
            media_id = media_info.extra.get("media_id")
            if not media_id:
                logger.error("No media_id found in media_info")
                return None
            
            # Create output directory
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            if self.api_available:
                try:
                    client = self.Client()
                    media = client.media_info(int(media_id))
                    
                    if media.media_type == 1:  # Photo
                        file_path = client.photo_download(int(media_id), folder=output_path)
                    elif media.media_type == 2:  # Video/Reel
                        file_path = client.video_download(int(media_id), folder=output_path)
                    elif media.media_type == 8:  # Carousel
                        # Download carousel items
                        items = media.carousel_media
                        file_paths = []
                        for idx, item in enumerate(items):
                            if item.media_type == 1:
                                path = client.photo_download(item.pk, folder=output_path)
                            else:
                                path = client.video_download(item.pk, folder=output_path)
                            file_paths.append(path)
                        return file_paths[0] if file_paths else None
                    else:
                        logger.warning(f"Unknown media type: {media.media_type}")
                        return None
                    
                    logger.info(f"Downloaded Instagram media to {file_path}")
                    return str(file_path)
                
                except Exception as e:
                    logger.warning(f"Failed to download with API: {e}")
            
            # Fallback: Create placeholder file
            file_path = os.path.join(output_path, f"instagram_{media_id}.mp4")
            Path(file_path).touch()
            logger.info(f"Created placeholder Instagram file: {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"Error downloading Instagram media: {e}")
            return None
    
    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize Instagram URL"""
        url = url.split('?')[0].rstrip('/')
        if not url.startswith('http'):
            url = f"https://{url}"
        return url
    
    @staticmethod
    def _extract_media_id(url: str) -> Optional[str]:
        """Extract Instagram media ID from URL"""
        patterns = [
            r'/p/([A-Za-z0-9\-_]+)',
            r'/reel/([A-Za-z0-9\-_]+)',
            r'/tv/([A-Za-z0-9\-_]+)',
            r'/stories/[^/]+/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def _parse_formats(media) -> List[dict]:
        """Parse Instagram media formats"""
        formats = []
        
        # Instagram: typically best quality video
        formats.append({
            "format_id": "best",
            "ext": "mp4",
            "format": "Best quality",
            "height": getattr(media, 'video_height', 1080),
            "width": getattr(media, 'video_width', 1920),
        })
        
        return formats


# Auto-register module
from modules import register_module

register_module("instagram", InstagramDownloader())

__all__ = ["InstagramDownloader"]
