"""
Pro Cache Database Models
مدل‌های پایگاه داده برای سیستم کش هوشمند
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, 
    BigInteger, ForeignKey, Index, JSON, Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta

Base = declarative_base()


class CachedDownload(Base):
    """
    جدول اصلی برای ذخیره اطلاعات کلی محتوای کش شده
    """
    __tablename__ = "cached_downloads"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # URL Information
    url_hash = Column(String(64), unique=True, nullable=False, index=True)
    original_url = Column(String(500), nullable=False)
    platform = Column(String(50), nullable=False, index=True)  # youtube, instagram, etc
    
    # Content Metadata
    title = Column(String(255))
    description = Column(String(1000))
    thumbnail_url = Column(String(500))
    duration = Column(Integer)  # در ثانیه
    uploader = Column(String(100))
    upload_date = Column(DateTime)
    
    # Cache Management
    created_at = Column(DateTime, default=func.now())
    last_accessed = Column(DateTime, default=func.now())
    access_count = Column(Integer, default=0)
    is_valid = Column(Boolean, default=True)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    
    # Additional Data
    metadata = Column(JSON)  # اطلاعات اضافی به صورت JSON
    
    # Relationships
    qualities = relationship("CachedQuality", back_populates="download", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_url_hash', 'url_hash'),
        Index('idx_platform', 'platform'),
        Index('idx_expires_at', 'expires_at'),
        Index('idx_access_count', 'access_count'),
        Index('idx_last_accessed', 'last_accessed'),
    )
    
    def __repr__(self):
        return f"<CachedDownload(id={self.id}, platform={self.platform}, title={self.title[:30]}...)>"


class CachedQuality(Base):
    """
    جدول برای ذخیره کیفیت‌های مختلف هر محتوا
    """
    __tablename__ = "cached_qualities"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    cache_id = Column(Integer, ForeignKey('cached_downloads.id'), nullable=False, index=True)
    
    # Quality Information
    quality_label = Column(String(50), nullable=False)  # "1080p HD", "720p", "320kbps", etc
    format_id = Column(String(50))  # شناسه فرمت در yt-dlp
    resolution = Column(String(20))  # "1920x1080"
    extension = Column(String(10))  # "mp4", "mp3", etc
    
    # File Information
    file_size = Column(BigInteger)  # اندازه فایل به بایت
    telegram_file_id = Column(String(255), unique=True, nullable=False, index=True)
    telegram_file_unique_id = Column(String(100))
    
    # Technical Details
    mime_type = Column(String(50))  # "video/mp4", "audio/mpeg"
    video_codec = Column(String(50))  # "h264", "vp9"
    audio_codec = Column(String(50))  # "aac", "opus"
    bitrate = Column(Integer)  # کیفیت صدا/ویدیو
    fps = Column(Integer)  # فریم در ثانیه
    
    # Statistics
    created_at = Column(DateTime, default=func.now())
    download_count = Column(Integer, default=0)
    last_downloaded = Column(DateTime)
    
    # Relationships
    download = relationship("CachedDownload", back_populates="qualities")
    
    # Indexes
    __table_args__ = (
        Index('idx_cache_id', 'cache_id'),
        Index('idx_quality_label', 'quality_label'),
        Index('idx_file_id', 'telegram_file_id'),
    )
    
    def __repr__(self):
        return f"<CachedQuality(id={self.id}, label={self.quality_label}, size={self.file_size})>"


class CacheStatistics(Base):
    """
    جدول برای ذخیره آمار روزانه سیستم کش
    """
    __tablename__ = "cache_statistics"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Date
    date = Column(DateTime, nullable=False, unique=True, index=True)
    
    # Hit/Miss Statistics
    total_requests = Column(Integer, default=0)
    cache_hits = Column(Integer, default=0)
    cache_misses = Column(Integer, default=0)
    hit_rate = Column(Float)  # درصد موفقیت
    
    # Storage Statistics
    total_cached_files = Column(Integer, default=0)
    total_cache_size = Column(BigInteger, default=0)  # به بایت
    new_files_added = Column(Integer, default=0)
    files_removed = Column(Integer, default=0)
    
    # Performance Statistics
    avg_response_time_hit = Column(Float)  # میلی‌ثانیه
    avg_response_time_miss = Column(Float)  # میلی‌ثانیه
    total_bandwidth_saved = Column(BigInteger, default=0)  # بایت
    
    # User Statistics
    unique_users = Column(Integer, default=0)
    top_platform = Column(String(50))
    most_requested_quality = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<CacheStatistics(date={self.date}, hits={self.cache_hits}, misses={self.cache_misses})>"


class CacheAccessLog(Base):
    """
    جدول لاگ دسترسی‌ها برای تحلیل دقیق‌تر
    """
    __tablename__ = "cache_access_logs"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Request Information
    user_id = Column(BigInteger, nullable=False, index=True)
    url_hash = Column(String(64), index=True)
    platform = Column(String(50))
    
    # Result
    cache_hit = Column(Boolean, nullable=False)
    quality_requested = Column(String(50))
    quality_served = Column(String(50))
    
    # Performance
    response_time = Column(Float)  # میلی‌ثانیه
    bytes_saved = Column(BigInteger, default=0)
    
    # Timestamp
    accessed_at = Column(DateTime, default=func.now(), index=True)
    
    # Indexes for analytics
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_accessed_at', 'accessed_at'),
        Index('idx_cache_hit', 'cache_hit'),
    )


class CacheConfiguration(Base):
    """
    جدول تنظیمات سیستم کش
    """
    __tablename__ = "cache_configuration"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Settings
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(500))
    value_type = Column(String(20))  # int, string, bool, json
    
    # Metadata
    description = Column(String(500))
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_by = Column(String(100))
    
    def __repr__(self):
        return f"<CacheConfiguration(key={self.key}, value={self.value})>"


# Default configuration values
DEFAULT_CONFIGS = [
    {
        'key': 'max_cache_size_gb',
        'value': '100',
        'value_type': 'int',
        'description': 'حداکثر حجم کش به گیگابایت'
    },
    {
        'key': 'default_ttl_days',
        'value': '30',
        'value_type': 'int',
        'description': 'مدت زمان نگهداری پیش‌فرض به روز'
    },
    {
        'key': 'cleanup_interval_hours',
        'value': '6',
        'value_type': 'int',
        'description': 'فاصله زمانی اجرای cleanup به ساعت'
    },
    {
        'key': 'min_file_size_to_cache_mb',
        'value': '1',
        'value_type': 'int',
        'description': 'حداقل حجم فایل برای کش کردن به مگابایت'
    },
    {
        'key': 'enable_redis_cache',
        'value': 'true',
        'value_type': 'bool',
        'description': 'فعال/غیرفعال کردن Redis cache'
    },
    {
        'key': 'redis_ttl_hours',
        'value': '24',
        'value_type': 'int',
        'description': 'مدت زمان نگهداری در Redis به ساعت'
    },
    {
        'key': 'platforms_enabled',
        'value': '["youtube", "instagram", "tiktok", "twitter"]',
        'value_type': 'json',
        'description': 'پلتفرم‌های فعال برای کش'
    }
]