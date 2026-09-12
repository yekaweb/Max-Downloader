"""
Google Account Pool Model for Crowdsourced Passkey & Cookie Load Balancing.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, BigInteger, func
from sqlalchemy.orm import relationship
from .models import Base


class GoogleAccount(Base):
    """
    Represents an idle Gmail account donated by a user to provide session cookies
    and PO-Tokens for YouTube scraping without botguard interference.
    """
    __tablename__ = "google_accounts"

    id = Column(Integer, primary_key=True, index=True)
    donor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # Account status: active, warming_up, refresh_needed, cooldown, suspended
    status = Column(String(50), default="active", index=True)
    passkey_registered = Column(Boolean, default=True)
    
    # Session state
    cookies_json = Column(Text, nullable=True)  # JSON-encoded Playwright / Netscape cookies
    po_token = Column(String(500), nullable=True)
    visitor_data = Column(String(500), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Usage metrics
    total_downloads_served = Column(Integer, default=0)
    daily_downloads_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    last_refreshed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    donor = relationship("User", backref="donated_google_accounts")


__all__ = ["GoogleAccount"]
