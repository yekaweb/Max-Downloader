"""Database Models - All models for DLBot"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger, Text, Float, func, ForeignKey, Enum as SQLEnum, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


# ============================================================================
# USER MODEL
# ============================================================================
class User(Base):
    """User model with referral and milestone tracking"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    telegram_username = Column(String(255), nullable=True, index=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False, index=True)
    is_blocked = Column(Boolean, default=False, index=True)
    
    language = Column(String(10), default="fa")
    preferred_quality = Column(String(50), default="best")
    
    total_downloads = Column(Integer, default=0)
    total_coins = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    
    # Referral system
    referral_code = Column(String(20), unique=True, nullable=True, index=True)
    referred_by = Column(BigInteger, nullable=True, index=True)
    referral_count = Column(Integer, default=0)
    referral_milestone = Column(Integer, default=0)  # Last milestone reached (1, 5, 10, 20, 50)
    referral_badge = Column(String(50), nullable=True)  # Current badge (e.g., "⭐ دوستیابی ستاره")
    
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_active_at = Column(DateTime, nullable=True)
    
    bio = Column(Text, nullable=True)



# ============================================================================
# DOWNLOAD HISTORY MODEL
# ============================================================================
class Download(Base):
    """Download history"""
    __tablename__ = "downloads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    url = Column(String(500), nullable=False)
    title = Column(String(500), nullable=True)
    module_type = Column(String(50), nullable=False)  # youtube, instagram, etc.
    
    file_size = Column(Integer, nullable=True)
    format = Column(String(100), nullable=True)
    quality = Column(String(50), nullable=True)
    
    status = Column(String(50), default="pending")  # pending, completed, failed
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now(), index=True)
    completed_at = Column(DateTime, nullable=True)


# ============================================================================
# CACHED FILE MODEL (for Telegram file_id caching)
# ============================================================================
class CachedFile(Base):
    """Cached Telegram files - prevents duplicate downloads and enables fast lookups"""
    __tablename__ = "cached_files"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Content identifiers (must match to prevent duplicates)
    file_hash = Column(String(256), nullable=False, index=True)
    url_hash = Column(String(256), nullable=True, index=True)  # Hash of source URL
    format_id = Column(String(50), nullable=True)  # Format identifier (e.g., video codec)
    codec = Column(String(50), nullable=True)  # Audio/Video codec (e.g., h264, aac)
    
    # Telegram file reference
    telegram_file_id = Column(String(255), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=True)
    
    # Video/Platform identifiers for quick lookup
    platform = Column(String(50), nullable=True, index=True)  # youtube, instagram, etc.
    video_id = Column(String(255), nullable=True, index=True)  # Platform-specific ID
    
    # Storage info
    local_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Table constraints
    __table_args__ = (
        # Unique constraint: same URL + format + codec = same file (avoid duplicates)
        UniqueConstraint('url_hash', 'format_id', 'codec', 
                        name='uq_cached_files_lookup'),
        # Indexes for quick lookup by platform
        Index('ix_cached_files_platform_video', 'platform', 'video_id'),
        Index('ix_cached_files_telegram_id', 'telegram_file_id'),
    )


# ============================================================================
# PLAN MODEL
# ============================================================================
class Plan(Base):
    """Subscription plans"""
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    monthly_price = Column(Float, nullable=False)
    yearly_price = Column(Float, nullable=True)
    
    # Features
    download_limit = Column(Integer, nullable=True)  # None = unlimited
    max_file_size = Column(Integer, nullable=True)  # None = unlimited
    quality_limit = Column(String(50), nullable=True)  # best, 720p, etc.
    
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, server_default=func.now())


# ============================================================================
# SUBSCRIPTION MODEL
# ============================================================================
class Subscription(Base):
    """User subscriptions"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    plan = relationship("Plan", backref="subscriptions")
    
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


# ============================================================================
# REFERRAL MODEL
# ============================================================================
class Referral(Base):
    """Referral tracking"""
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    referred_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    status = Column(String(50), default="pending")  # pending, completed, revoked
    reward_coins = Column(Float, default=0.0)
    
    created_at = Column(DateTime, server_default=func.now(), index=True)
    completed_at = Column(DateTime, nullable=True)


# ============================================================================
# COIN TRANSACTION MODEL
# ============================================================================
class CoinTransaction(Base):
    """Coin transactions"""
    __tablename__ = "coin_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # earn, spend, referral, etc.
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now(), index=True)


# ============================================================================
# PAYMENT TRANSACTION MODEL
# ============================================================================
class Payment(Base):
    """Payment transactions"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")  # USD, IRR, etc.
    
    payment_method = Column(String(50), nullable=False)  # cryptobot, zarinpal, etc.
    status = Column(String(50), default="pending")  # pending, completed, failed, cancelled
    
    transaction_id = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    completed_at = Column(DateTime, nullable=True)


# ============================================================================
# CHANNEL MODEL (for force-join)
# ============================================================================
class Channel(Base):
    """Force-join channels"""
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(BigInteger, unique=True, nullable=False, index=True)
    channel_username = Column(String(255), nullable=True)
    channel_name = Column(String(255), nullable=False)
    
    invite_link = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime, server_default=func.now())


__all__ = [
    "Base",
    "User",
    "Download",
    "CachedFile",
    "Plan",
    "Subscription",
    "Referral",
    "CoinTransaction",
    "Payment",
    "Channel",
]
