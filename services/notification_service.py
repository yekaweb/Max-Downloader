"""Notification service

Lightweight notification methods used during testing and import-time
checks. These stubs log actions and return success booleans so other
parts of the system can call them without requiring the Telegram
integration to be configured.
"""
try:
    from loguru import logger
except Exception:
    import logging

    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
from sqlalchemy.ext.asyncio import AsyncSession


class NotificationService:
    def __init__(self, db: AsyncSession | None = None):
        self.db = db

    async def send_subscription_reminder(self, user_id: int) -> bool:
        """Send subscription expiration reminder (stub)."""
        logger.info("send_subscription_reminder -> user_id={}", user_id)
        return True

    async def send_download_notification(self, user_id: int, title: str) -> bool:
        """Notify user of completed download (stub)."""
        logger.info("send_download_notification -> user_id={}, title={}", user_id, title)
        return True

    async def send_referral_reward(self, user_id: int, coins: float) -> bool:
        """Notify user of referral reward (stub)."""
        logger.info("send_referral_reward -> user_id={}, coins={}", user_id, coins)
        return True


__all__ = ["NotificationService"]
