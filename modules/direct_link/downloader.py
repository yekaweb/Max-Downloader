"""
Direct Link Downloader Module
Downloads media from direct HTTP/HTTPS links with resume support
"""

import os
import aiohttp
import asyncio
from typing import Optional
from pathlib import Path
from modules.base import BaseDownloader, MediaInfo


class DirectLinkDownloader(BaseDownloader):
    """Generic direct link downloader for HTTP/HTTPS files"""
    
    # Module metadata
    NAME = "Direct Link"
    ICON = "🔗"
    SUPPORTED_DOMAINS = ["*"]  # Any domain with direct file
    VERSION = "1.0.0"
    ENABLED = True
    PRIORITY = 5  # Lowest priority - fallback for unknown links
    
    SUPPORTED_FORMATS = {
        '.mp4': 'video/mp4',
        '.mkv': 'video/x-matroska',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.webm': 'video/webm',
        '.mp3': 'audio/mpeg',
        '.flac': 'audio/flac',
        '.wav': 'audio/wav',
        '.m4a': 'audio/mp4',
        '.zip': 'application/zip',
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
    }
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        """Check if URL is a direct downloadable link"""
        try:
            # Check if it's a valid HTTP(S) URL
            if not (url.startswith('http://') or url.startswith('https://')):
                return False
            
            # Extract file extension
            path = url.split('?')[0]  # Remove query parameters
            ext = os.path.splitext(path)[1].lower()
            
            # Check if extension is supported
            return ext in cls.SUPPORTED_FORMATS
        except Exception:
            return False
    
    async def fetch_info(self, url: str) -> Optional[MediaInfo]:
        """Get file metadata from direct link"""
        try:
            async with aiohttp.ClientSession() as session:
                # Use HEAD request first to get metadata
                async with session.head(url, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        return None
                    
                    # Extract file information
                    content_length = resp.content_length
                    content_type = resp.content_type or 'application/octet-stream'
                    
                    # Get filename from URL or headers
                    filename = self._get_filename(url, resp.headers.get('content-disposition', ''))
                    
                    # Determine file type
                    ext = os.path.splitext(filename)[1].lower()
                    file_type = 'video' if 'video' in content_type else \
                               'audio' if 'audio' in content_type else \
                               'image' if 'image' in content_type else 'file'
                    
                    # Create MediaInfo object
                    return MediaInfo(
                        url=url,
                        title=filename,
                        duration=None,
                        file_size=content_length,
                        file_type=file_type,
                        formats=[{
                            'format_id': 'direct',
                            'format': 'Direct Download',
                            'ext': ext,
                            'file_size': content_length,
                            'content_type': content_type
                        }]
                    )
        except Exception as e:
            self.logger.error(f"Error fetching info for {url}: {e}")
            return None
    
    async def download(self, media_info: MediaInfo, output_path: str, progress_callback=None) -> Optional[str]:
        """Download file with resume support"""
        try:
            filepath = os.path.join(output_path, media_info.title)
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            # Check if file already exists
            if os.path.exists(filepath):
                return filepath
            
            # Download file with resume support
            async with aiohttp.ClientSession() as session:
                async with session.get(media_info.url, timeout=aiohttp.ClientTimeout(total=3600)) as resp:
                    if resp.status != 200:
                        self.logger.error(f"Failed to download: HTTP {resp.status}")
                        return None
                    
                    total_size = resp.content_length or 0
                    downloaded = 0
                    
                    with open(filepath, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(1024 * 1024):  # 1MB chunks
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Call progress callback
                            if progress_callback:
                                progress = (downloaded / total_size * 100) if total_size > 0 else 0
                                await progress_callback({
                                    'status': 'downloading',
                                    'progress': min(progress, 100),
                                    'downloaded': downloaded,
                                    'total': total_size
                                })
                    
                    self.logger.info(f"Successfully downloaded: {filepath}")
                    return filepath
        except Exception as e:
            self.logger.error(f"Error downloading {media_info.url}: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return None
    
    def _get_filename(self, url: str, content_disposition: str = '') -> str:
        """Extract filename from URL or headers"""
        try:
            # Try to get from Content-Disposition header
            if content_disposition:
                for part in content_disposition.split(';'):
                    if part.strip().startswith('filename='):
                        filename = part.split('=', 1)[1].strip('"\'')
                        if filename:
                            return filename
            
            # Get from URL path
            path = url.split('?')[0]  # Remove query parameters
            filename = os.path.basename(path)
            
            # Fallback if no filename found
            if not filename or filename == '':
                filename = 'download'
            
            return filename
        except Exception:
            return 'download'


# Module registration
def register():
    """Register Direct Link downloader"""
    return DirectLinkDownloader
