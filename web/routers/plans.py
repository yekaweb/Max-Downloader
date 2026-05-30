"""Plans API routes - Subscription management"""
import logging
from typing import Dict, Any, List

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class PlanCreate(BaseModel):
    """Plan creation model"""

    name: str
    description: str
    price: float
    currency: str = "USD"
    features: List[str]
    max_downloads_daily: int
    max_file_size_gb: int
    enabled: bool = True


@router.get("/")
async def list_plans() -> dict:
    """Get all subscription plans"""
    plans = [
        {
            "id": "free",
            "name": "Free",
            "description": "Limited access",
            "price": 0,
            "currency": "USD",
            "features": [
                "1 download per day",
                "Max 100MB files",
                "Limited quality",
            ],
            "max_downloads_daily": 1,
            "max_file_size_gb": 0.1,
            "subscribers": 1012,
            "active": True,
        },
        {
            "id": "premium",
            "name": "Premium",
            "description": "Full access",
            "price": 9.99,
            "currency": "USD",
            "features": [
                "20 downloads per day",
                "Up to 2GB files",
                "Full quality",
                "No ads",
            ],
            "max_downloads_daily": 20,
            "max_file_size_gb": 2,
            "subscribers": 215,
            "active": True,
        },
        {
            "id": "vip",
            "name": "VIP",
            "description": "Ultimate access",
            "price": 24.99,
            "currency": "USD",
            "features": [
                "Unlimited downloads",
                "Up to 4GB files",
                "Best quality",
                "Priority support",
                "Custom features",
            ],
            "max_downloads_daily": 999999,
            "max_file_size_gb": 4,
            "subscribers": 23,
            "active": True,
        },
    ]

    return {
        "total": len(plans),
        "plans": plans,
    }


@router.get("/{plan_id}")
async def get_plan(plan_id: str) -> dict:
    """Get specific plan details"""
    return {
        "id": plan_id,
        "name": "Premium",
        "description": "Full access to all features",
        "price": 9.99,
        "currency": "USD",
        "features": [
            "20 downloads per day",
            "Up to 2GB files",
            "Full quality",
            "No ads",
        ],
        "max_downloads_daily": 20,
        "max_file_size_gb": 2,
        "subscribers": 215,
        "revenue_monthly": 2147.85,
        "revenue_total": 18942.15,
        "created_at": "2026-01-01T00:00:00",
        "active": True,
    }


@router.post("/")
async def create_plan(plan: PlanCreate) -> dict:
    """Create new subscription plan"""
    logger.info(f"Creating plan: {plan.name}")

    return {
        "success": True,
        "plan": {
            "id": "plan_new_123",
            **plan.dict(),
            "created_at": "2026-05-23T12:00:00",
        },
    }


@router.put("/{plan_id}")
async def update_plan(plan_id: str, plan: PlanCreate) -> dict:
    """Update plan"""
    logger.info(f"Updating plan: {plan_id}")

    return {
        "success": True,
        "plan": {
            "id": plan_id,
            **plan.dict(),
            "updated_at": "2026-05-23T12:00:00",
        },
    }


@router.delete("/{plan_id}")
async def delete_plan(plan_id: str) -> dict:
    """Delete plan"""
    logger.warning(f"Deleting plan: {plan_id}")

    return {
        "success": True,
        "message": f"Plan {plan_id} deleted",
    }


@router.get("/{plan_id}/analytics")
async def get_plan_analytics(plan_id: str) -> dict:
    """Get plan analytics"""
    return {
        "plan_id": plan_id,
        "total_subscribers": 215,
        "new_subscribers_today": 5,
        "churn_rate": 2.3,
        "monthly_revenue": 2147.85,
        "average_subscriber_lifetime_value": 88.23,
        "popular_platforms": ["youtube", "instagram"],
    }


@router.get("/stats/summary")
async def get_plans_summary() -> dict:
    """Get plans statistics summary"""
    return {
        "total_plans": 3,
        "total_subscribers": 1250,
        "total_monthly_revenue": 2400.00,
        "total_annual_revenue": 28800.00,
        "premium_conversion_rate": 17.2,
    }


__all__ = ["router", "PlanCreate"]
