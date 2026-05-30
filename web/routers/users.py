"""Users API routes - User management"""
import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
) -> dict:
    """
    List users with pagination and search

    Args:
        skip: Number of users to skip
        limit: Max number of users to return
        search: Search query (username, email, or telegram_id)

    Returns:
        List of users with pagination info
    """
    # Mock data
    users = [
        {
            "id": 1,
            "user_id": 123456789,
            "username": "user1",
            "language": "fa",
            "plan": "premium",
            "downloads": 45,
            "created_at": "2026-01-15T10:30:00",
            "last_active": "2026-05-23T12:00:00",
        },
        {
            "id": 2,
            "user_id": 987654321,
            "username": "user2",
            "language": "en",
            "plan": "free",
            "downloads": 12,
            "created_at": "2026-02-20T14:20:00",
            "last_active": "2026-05-22T18:30:00",
        },
    ]

    return {
        "total": 1250,
        "skip": skip,
        "limit": limit,
        "users": users,
    }


@router.get("/{user_id}")
async def get_user(user_id: int) -> dict:
    """Get detailed user information"""
    # Mock data
    return {
        "id": user_id,
        "user_id": 123456789,
        "username": "testuser",
        "language": "fa",
        "plan": "premium",
        "subscription_active": True,
        "downloads": 45,
        "coins_balance": 1500,
        "referral_code": "ABC123DEF456",
        "referrals_count": 5,
        "created_at": "2026-01-15T10:30:00",
        "last_active": "2026-05-23T12:00:00",
        "stats": {
            "total_downloaded_gb": 125.5,
            "total_download_time_hours": 48.3,
            "favorite_platforms": ["youtube", "instagram"],
        },
    }


@router.post("/{user_id}/ban")
async def ban_user(user_id: int, reason: Optional[str] = None) -> dict:
    """Ban a user"""
    logger.warning(f"User {user_id} banned. Reason: {reason}")
    return {
        "success": True,
        "message": f"User {user_id} has been banned",
    }


@router.post("/{user_id}/unban")
async def unban_user(user_id: int) -> dict:
    """Unban a user"""
    logger.info(f"User {user_id} unbanned")
    return {
        "success": True,
        "message": f"User {user_id} has been unbanned",
    }


@router.post("/{user_id}/plan")
async def update_user_plan(user_id: int, plan_id: str) -> dict:
    """Change user subscription plan"""
    logger.info(f"User {user_id} plan changed to {plan_id}")
    return {
        "success": True,
        "message": f"User plan updated to {plan_id}",
        "user_id": user_id,
        "plan": plan_id,
    }


@router.post("/{user_id}/coins")
async def add_coins_to_user(user_id: int, amount: int, reason: str) -> dict:
    """Add coins to user account"""
    logger.info(f"Added {amount} coins to user {user_id}. Reason: {reason}")
    return {
        "success": True,
        "message": f"{amount} coins added to user {user_id}",
        "user_id": user_id,
        "coins_added": amount,
        "new_balance": 1500 + amount,
    }


@router.get("/stats/summary")
async def get_users_summary() -> dict:
    """Get user statistics summary"""
    return {
        "total_users": 1250,
        "active_users_today": 342,
        "new_users_today": 45,
        "premium_users": 238,
        "free_users": 1012,
        "banned_users": 15,
        "average_downloads_per_user": 12.3,
    }


__all__ = ["router"]
