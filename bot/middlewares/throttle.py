"""Throttle middleware - Anti-spam protection"""
import logging
from typing import Callable, Any, Dict
from datetime import datetime, timedelta

from aiogram import BaseMiddleware
from aiogram.types import Message, Update, User
from aioredis import Redis

logger = logging.getLogger(__name__)


class ThrottleMiddleware(BaseMiddleware):
    """
    Throttle middleware - Prevents users from spamming commands.

    Implements rate limiting based on:
    - User commands (max X commands per Y seconds)
    - Specific command throttling
    - Handler-specific throttling
    """

    def __init__(
        self,
        redis_client: Redis,
        default_rate: int = 2,  # commands per window
        default_window: int = 5,  # seconds
    ):
        """
        Initialize throttle middleware

        Args:
            redis_client: Redis client for tracking throttle data
            default_rate: Max commands per window
            default_window: Time window in seconds
        """
        self.redis = redis_client
        self.default_rate = default_rate
        self.default_window = default_window

        # Command-specific throttle limits
        self.command_limits = {
            "start": {"rate": 1, "window": 60},  # 1 per minute
            "help": {"rate": 2, "window": 60},  # 2 per minute
            "download": {"rate": 5, "window": 60},  # 5 per minute
            "stats": {"rate": 1, "window": 60},  # Admin: 1 per minute
            "broadcast": {"rate": 1, "window": 300},  # Admin: 1 per 5 minutes
        }

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Any],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        """Middleware handler"""
        message = event.message
        if not message or not message.from_user:
            return await handler(event, data)

        user_id = message.from_user.id
        command = None

        # Extract command if message is a command
        if message.text and message.text.startswith("/"):
            command = message.text.split()[0][1:]  # Remove leading /

        # Check throttle
        is_throttled = await self.check_throttle(user_id, command)

        if is_throttled:
            # Log throttle
            logger.warning(f"User {user_id} throttled - command: {command}")

            # Send warning message
            throttle_msg = (
                "⏱ <b>Too fast!</b>\n\n"
                "You're sending commands too quickly.\n"
                "Please wait a moment and try again.\n\n"
                "<i>This is to prevent spam.</i>"
            )

            try:
                await message.reply(throttle_msg, parse_mode="HTML")
            except Exception as e:
                logger.error(f"Error sending throttle message: {e}")

            return  # Don't call handler

        # Update throttle counter
        await self.record_request(user_id, command)

        # Call handler
        return await handler(event, data)

    async def check_throttle(self, user_id: int, command: Optional[str] = None) -> bool:
        """
        Check if user is throttled

        Args:
            user_id: User ID
            command: Command name (optional)

        Returns:
            True if throttled, False otherwise
        """
        # Get rate limits
        if command and command in self.command_limits:
            rate, window = (
                self.command_limits[command]["rate"],
                self.command_limits[command]["window"],
            )
        else:
            rate, window = self.default_rate, self.default_window

        # Build Redis key
        key = f"throttle:{user_id}"
        if command:
            key += f":{command}"

        try:
            # Get current count
            count = await self.redis.get(key)
            count = int(count) if count else 0

            # Check if throttled
            if count >= rate:
                return True

            return False

        except Exception as e:
            logger.error(f"Throttle check error: {e}")
            # On error, don't throttle to avoid breaking functionality
            return False

    async def record_request(
        self, user_id: int, command: Optional[str] = None
    ) -> None:
        """
        Record user request for throttling

        Args:
            user_id: User ID
            command: Command name (optional)
        """
        # Get rate limits
        if command and command in self.command_limits:
            rate, window = (
                self.command_limits[command]["rate"],
                self.command_limits[command]["window"],
            )
        else:
            rate, window = self.default_rate, self.default_window

        # Build Redis key
        key = f"throttle:{user_id}"
        if command:
            key += f":{command}"

        try:
            # Increment counter
            await self.redis.incr(key)

            # Set expiry if not set
            ttl = await self.redis.ttl(key)
            if ttl == -1:  # No expiry set
                await self.redis.expire(key, window)

        except Exception as e:
            logger.error(f"Error recording throttle request: {e}")

    async def reset_user_throttle(self, user_id: int) -> None:
        """Reset throttle for a user (useful for vip users)"""
        try:
            keys = await self.redis.keys(f"throttle:{user_id}*")
            for key in keys:
                await self.redis.delete(key)
            logger.info(f"Reset throttle for user {user_id}")
        except Exception as e:
            logger.error(f"Error resetting throttle: {e}")


__all__ = ["ThrottleMiddleware"]
