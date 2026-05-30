"""
Database Models - User Model
Defines the User database schema
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger, Text, Float, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model for storing user information and subscription data"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Telegram info
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False, doc="Telegram user ID")
    telegram_username = Column(String(255), nullable=True, index=True, doc="Telegram username")
    first_name = Column(String(255), nullable=True, doc="First name")
    last_name = Column(String(255), nullable=True, doc="Last name")
    phone_number = Column(String(20), nullable=True, doc="Phone number")
    
    # User status
    is_active = Column(Boolean, default=True, index=True, doc="Account active status")
    is_admin = Column(Boolean, default=False, index=True, doc="Admin privileges")
    is_blocked = Column(Boolean, default=False, index=True, doc="User blocked status")
    
    # User preferences
    language = Column(String(10), default="fa", doc="Preferred language (fa, en, ar, ru, zh)")
    preferred_quality = Column(String(50), default="best", doc="Preferred download quality")
    
    # Statistics
    total_downloads = Column(Integer, default=0, doc="Total number of downloads")
    total_coins = Column(Float, default=0.0, doc="Coin balance")
    total_spent = Column(Float, default=0.0, doc="Total amount spent on subscriptions")
    
    # Referral info
    referral_code = Column(String(20), unique=True, nullable=True, index=True, doc="User's unique referral code")
    referred_by = Column(BigInteger, nullable=True, index=True, doc="Telegram ID of referring user")
    referral_count = Column(Integer, default=0, doc="Number of successful referrals")
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True, doc="Account creation date")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), doc="Last update date")
    last_active_at = Column(DateTime, nullable=True, doc="Last activity date")
    
    # About
    bio = Column(Text, nullable=True, doc="User bio/description")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.telegram_username})>"


__all__ = ["User", "Base"]
