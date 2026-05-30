"""Subscription status check middleware - verify user subscription status"""

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User, Subscription
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    """
    Middleware to check user subscription status.
    Attaches subscription info to user context.
    """
    
    async def __call__(self, handler, event: Update, data: dict):
        """Process middleware"""
        
        # Get user and session
        user = None
        session: AsyncSession = data.get("session")
        
        if isinstance(event.message, Message):
            user = event.message.from_user
        elif isinstance(event.callback_query, CallbackQuery):
            user = event.callback_query.from_user
        
        # If no user or session, skip
        if not user or not session:
            return await handler(event, data)
        
        try:
            # Get user from database
            result = await session.execute(
                select(User).where(User.telegram_id == user.id)
            )
            db_user = result.scalars().first()
            
            if not db_user:
                return await handler(event, data)
            
            # Get active subscription
            sub_result = await session.execute(
                select(Subscription).where(
                    Subscription.user_id == db_user.id,
                    Subscription.expires_at > datetime.utcnow()
                )
            )
            active_subscription = sub_result.scalars().first()
            
            # Attach to data
            data["subscription"] = active_subscription
            data["user"] = db_user
            data["is_premium"] = active_subscription is not None
            
            if active_subscription:
                data["subscription_plan"] = active_subscription.plan
                data["days_remaining"] = (
                    active_subscription.expires_at - datetime.utcnow()
                ).days
            
        except Exception as e:
            logger.error(f"Error in subscription middleware: {e}")
            # Continue even if error occurs
        
        return await handler(event, data)


class ForceJoinMiddleware(BaseMiddleware):
    """
    Middleware to check if user joined required channels.
    Blocks access until user joins all mandatory channels.
    """
    
    async def __call__(self, handler, event: Update, data: dict):
        """Process middleware"""
        
        # Get user and session
        user = None
        session: AsyncSession = data.get("session")
        
        if isinstance(event.message, Message):
            user = event.message.from_user
        elif isinstance(event.callback_query, CallbackQuery):
            user = event.callback_query.from_user
        
        # Skip for /start command (user needs to see join prompt)
        if isinstance(event.message, Message) and event.message.text:
            if event.message.text.startswith("/start"):
                return await handler(event, data)
        
        if not user or not session:
            return await handler(event, data)
        
        try:
            from database.models import Channel
            from bot.loader import bot
            
            # Get required channels
            result = await session.execute(
                select(Channel).where(Channel.required == True)
            )
            required_channels = result.scalars().all()
            
            if not required_channels:
                # No required channels, continue
                return await handler(event, data)
            
            # Check if user is member of all required channels
            all_joined = True
            missing_channels = []
            
            for channel in required_channels:
                try:
                    member = await bot.get_chat_member(
                        chat_id=channel.telegram_id,
                        user_id=user.id
                    )
                    # Check if user is not kicked or left
                    if member.status in ["left", "kicked"]:
                        all_joined = False
                        missing_channels.append(channel)
                except Exception as e:
                    logger.warning(f"Error checking channel membership: {e}")
                    all_joined = False
                    missing_channels.append(channel)
            
            data["force_join_required"] = not all_joined
            data["missing_channels"] = missing_channels
            
            # Continue handler regardless
            # Handler will check force_join_required flag
            
        except Exception as e:
            logger.error(f"Error in force-join middleware: {e}")
        
        return await handler(event, data)
