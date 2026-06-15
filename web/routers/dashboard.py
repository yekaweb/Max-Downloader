"""Dashboard API routes - Bot statistics and metrics"""
import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from database.connection import AsyncSessionLocal
from services.stats_service import StatsService
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/overview")
async def get_dashboard_overview(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Get dashboard overview with key metrics
    """
    stats_service = StatsService(db)
    
    total_users = await stats_service.get_total_users()
    active_today = await stats_service.get_active_users_today()
    total_downloads = await stats_service.get_total_downloads()
    total_revenue = await stats_service.get_total_revenue()
    
    overview = {
        "users": {
            "total": total_users,
            "active_today": active_today,
            "new_today": 0, # Placeholder
            "premium": 0, # Placeholder
        },
        "downloads": {
            "total": total_downloads,
            "today": 0, # Placeholder
            "this_week": 0,
            "this_month": 0,
        },
        "revenue": {
            "today": 0.0,
            "this_week": 0.0,
            "this_month": total_revenue,
        },
        "server": {
            "cpu_usage": 32,
            "memory_usage": 58,
            "disk_usage": 72,
            "uptime_hours": 144,
        },
    }

    return overview


@router.get("/stats")
async def get_statistics(period: str = "week") -> dict:
    """
    Get detailed statistics for a time period

    Args:
        period: 'day', 'week', 'month', 'year'

    Returns:
        Detailed statistics
    """
    period_mapping = {
        "day": 1,
        "week": 7,
        "month": 30,
        "year": 365,
    }

    days = period_mapping.get(period, 7)

    stats = {
        "period": period,
        "days": days,
        "start_date": (datetime.now() - timedelta(days=days)).isoformat(),
        "end_date": datetime.now().isoformat(),
        "downloads": 523,
        "users": 342,
        "revenue": 2400.00,
        "average_download_time": 45,  # seconds
        "success_rate": 96.8,  # percentage
        "top_platforms": [
            {"name": "YouTube", "count": 412, "percentage": 78.8},
            {"name": "Instagram", "count": 78, "percentage": 14.9},
            {"name": "TikTok", "count": 33, "percentage": 6.3},
        ],
    }

    return stats


@router.get("/charts/downloads")
async def get_download_chart_data(days: int = 7) -> dict:
    """Get download data for charts"""
    # Mock data - would be calculated from database
    return {
        "labels": [f"Day {i}" for i in range(1, days + 1)],
        "datasets": [
            {
                "label": "Downloads",
                "data": [100 + i * 20 for i in range(days)],
                "borderColor": "rgb(75, 192, 192)",
                "tension": 0.1,
            }
        ],
    }


@router.get("/charts/revenue")
async def get_revenue_chart_data(days: int = 7) -> dict:
    """Get revenue data for charts"""
    return {
        "labels": [f"Day {i}" for i in range(1, days + 1)],
        "datasets": [
            {
                "label": "Revenue ($)",
                "data": [500 + i * 100 for i in range(days)],
                "borderColor": "rgb(75, 192, 192)",
                "tension": 0.1,
            }
        ],
    }


@router.get("/charts/users")
async def get_users_chart_data(days: int = 7) -> dict:
    """Get user growth data for charts"""
    return {
        "labels": [f"Day {i}" for i in range(1, days + 1)],
        "datasets": [
            {
                "label": "Total Users",
                "data": [1000 + i * 30 for i in range(days)],
                "borderColor": "rgb(255, 99, 132)",
                "tension": 0.1,
            }
        ],
    }


@router.get("/health")
async def get_health_status() -> dict:
    """Live health check – probes Redis, DB, and Bot."""
    from database.connection import AsyncSessionLocal
    from config import settings
    import time

    status = {}
    overall = "healthy"

    # ── Database ────────────────────────────────────────────────────
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(__import__("sqlalchemy", fromlist=["text"]).text("SELECT 1"))
        status["database"] = "healthy"
    except Exception as exc:
        logger.error(f"[Health] DB check failed: {exc}")
        status["database"] = "unhealthy"
        overall = "degraded"

    # ── Redis ───────────────────────────────────────────────────────
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.redis_url, socket_connect_timeout=2)
        await r.ping()
        await r.aclose()
        status["redis"] = "healthy"
    except Exception as exc:
        logger.error(f"[Health] Redis check failed: {exc}")
        status["redis"] = "unhealthy"
        overall = "degraded"

    # ── Telegram Bot API ─────────────────────────────────────────────
    try:
        from bot.loader import bot
        if bot:
            me = await bot.get_me()
            status["bot_api"] = f"connected (@{me.username})"
        else:
            status["bot_api"] = "bot not initialized"
            overall = "degraded"
    except Exception as exc:
        logger.error(f"[Health] Bot check failed: {exc}")
        status["bot_api"] = "unreachable"
        overall = "degraded"

    return {
        "status": overall,
        "checks": status,
        "timestamp": datetime.now().isoformat(),
    }


__all__ = ["router"]
