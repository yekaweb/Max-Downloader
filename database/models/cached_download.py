"""
Pro Cache Database Models - Smart Cache System
Two-table architecture:
  - CachedDownload: One row per URL (title, platform, metadata)
  - CachedQuality: One row per quality/format (file_id, size, codec)
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean,
    BigInteger, ForeignKey, Index, JSON, Float, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta

from database.models.models import Base


class CachedDownload(Base):
    """One row per URL - stores metadata shared across all qualities"""
    __tablename__ = "cached_downloads"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url_hash = Column(String(64), unique=True, nullable=False, index=True,
                      doc="SHA-256 hash of normalized URL")
    original_url = Column(String(2048), nullable=False,
                          doc="Original URL sent by user")
    normalized_url = Column(String(2048), nullable=True,
                            doc="Normalized URL (YouTube -> youtu.be unified)")
    platform = Column(String(50), nullable=False, index=True,
                      doc="Platform (youtube, instagram, tiktok, twitter)")
    title = Column(String(500), nullable=True, doc="Video/media title")
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    duration = Column(Integer, nullable=True, doc="Duration in seconds")
    uploader = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    last_accessed = Column(DateTime, default=func.now())
    access_count = Column(Integer, default=0)
    is_valid = Column(Boolean, default=True)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    metadata_json = Column(JSON, nullable=True)
    qualities = relationship(
        "CachedQuality", back_populates="download",
        cascade="all, delete-orphan", lazy="selectin"
    )
    __table_args__ = (
        Index("idx_cd_url_hash", "url_hash", unique=True),
        Index("idx_cd_platform", "platform"),
        Index("idx_cd_expires", "expires_at"),
        Index("idx_cd_access", "access_count"),
        Index("idx_cd_last_access", "last_accessed"),
    )
    def __repr__(self):
        return f"<CachedDownload(id={self.id}, platform={self.platform})>"


class CachedQuality(Base):
    """Each row = one format/quality of a cached URL"""
    __tablename__ = "cached_qualities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_id = Column(
        Integer, ForeignKey("cached_downloads.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    quality_label = Column(String(100), nullable=False,
                           doc="Human-readable: 1080p HD, 720p, 320kbps MP3")
    format_id = Column(String(50), nullable=True, doc="yt-dlp format identifier")
    resolution = Column(String(20), nullable=True, doc="e.g. 1920x1080")
    extension = Column(String(10), nullable=True, doc="Container: mp4, mkv, webm, m4a, mp3")
    file_size = Column(BigInteger, nullable=True, doc="File size in bytes (EXACT)")
    telegram_file_id = Column(String(255), unique=True, nullable=False, index=True,
                              doc="Telegram file_id for instant delivery")
    telegram_file_unique_id = Column(String(100), nullable=True)
    mime_type = Column(String(50), nullable=True, doc="MIME: video/mp4, audio/mpeg")
    video_codec = Column(String(50), nullable=True, doc="h264, vp9, av1")
    audio_codec = Column(String(50), nullable=True, doc="aac, opus, mp3")
    bitrate = Column(Integer, nullable=True, doc="Audio/video bitrate in kbps")
    fps = Column(Integer, nullable=True, doc="Frames per second")
    created_at = Column(DateTime, default=func.now())
    download_count = Column(Integer, default=0)
    last_downloaded = Column(DateTime, nullable=True)
    download = relationship("CachedDownload", back_populates="qualities")
    __table_args__ = (
        Index("idx_cq_cache_id", "cache_id"),
        Index("idx_cq_quality_label", "quality_label"),
        Index("idx_cq_file_id", "telegram_file_id"),
    )
    @property
    def file_size_mb(self) -> float:
        if self.file_size:
            return self.file_size / (1024 * 1024)
        return 0.0
    def __repr__(self):
        return f"<CachedQuality(id={self.id}, label={self.quality_label}, size={self.file_size_mb:.1f}MB)>"


__all__ = ["CachedDownload", "CachedQuality"]
