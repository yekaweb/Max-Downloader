"""
Cached Download Model - Store telegram_file_id and metadata
"""

from sqlalchemy import Column, String, Integer, DateTime, BigInteger, Text, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CachedDownload(Base):
    """
    Store cached downloads with telegram_file_id for fast re-delivery
    
    When user sends same URL again, bot shows cached versions instead of re-downloading
    """
    
    __tablename__ = "cached_downloads"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Source information
    source_url = Column(String(2048), unique=False, nullable=False, index=True, 
                       doc="Original URL (YouTube, Instagram, Twitter, etc)")
    source_platform = Column(String(50), nullable=False, index=True, 
                            doc="Platform (youtube, instagram, twitter, tiktok, etc)")
    
    # Video/Media info
    media_title = Column(String(500), nullable=False, 
                        doc="Video title/name (truncated to 500 chars)")
    media_duration = Column(Integer, nullable=True, 
                           doc="Video duration in seconds")
    media_uploader = Column(String(255), nullable=True, 
                           doc="Original video uploader name")
    
    # Downloaded file info
    telegram_file_id = Column(String(255), unique=True, nullable=False, index=True, 
                             doc="Telegram's file_id for this specific file")
    file_size = Column(BigInteger, nullable=False, 
                      doc="File size in bytes (EXACT size, not estimated)")
    file_type = Column(String(50), nullable=False, 
                      doc="MIME type (video/mp4, audio/mpeg, etc)")
    
    # Quality/format info
    quality = Column(String(100), nullable=False, 
                    doc="Resolution (1080p, 720p, etc) or audio bitrate (320kbps, 128kbps)")
    format_codec = Column(String(50), nullable=False, 
                         doc="Codec (h264, vp9, av1, mp3, aac, opus, etc)")
    format_container = Column(String(20), nullable=False, 
                             doc="Container (mp4, mkv, webm, m4a, etc)")
    
    # Video resolution (if applicable)
    resolution_width = Column(Integer, nullable=True, 
                             doc="Video width in pixels (1920 for 1080p, etc)")
    resolution_height = Column(Integer, nullable=True, 
                              doc="Video height in pixels (1080 for 1080p, etc)")
    
    # Metadata
    download_count = Column(Integer, default=1, 
                           doc="Number of times this cached file was used")
    last_used_at = Column(DateTime, nullable=True, 
                         doc="Last time this cached file was delivered to a user")
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True, 
                       doc="When this file was first cached")
    expires_at = Column(DateTime, nullable=True, 
                       doc="Cache expiration time (optional)")
    
    def __repr__(self):
        return (f"<CachedDownload(id={self.id}, url={self.source_url[:50]}..., "
                f"quality={self.quality}, size={self.file_size/1024/1024:.1f}MB)>")
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes"""
        return self.file_size / (1024 * 1024)
    
    @property
    def file_size_gb(self) -> float:
        """Get file size in gigabytes"""
        return self.file_size / (1024 * 1024 * 1024)
    
    @property
    def resolution_str(self) -> str:
        """Get resolution as string (1280x720, etc)"""
        if self.resolution_width and self.resolution_height:
            return f"{self.resolution_width}x{self.resolution_height}"
        return "N/A"


__all__ = ["CachedDownload", "Base"]
