"""
Tests for SubscriptionService – Plan Limits & Activation (Happy paths).
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy import func

from services.subscription_service import SubscriptionService


# ─────────────────────────────────────────────────────────────
# check_user_limits
# ─────────────────────────────────────────────────────────────

class TestCheckUserLimits:

    @pytest.mark.asyncio
    async def test_no_plan_returns_free_defaults(self, mock_db):
        """Users with no active plan get free-tier limits."""
        mock_db.execute.return_value.scalars.return_value.first.return_value = None

        svc = SubscriptionService(mock_db)
        limits = await svc.check_user_limits(user_id=42)

        assert limits["has_limits"] is True
        assert limits["daily_limit"] == 5
        assert limits["max_file_size"] == 50 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_premium_plan_returns_plan_limits(self, mock_db):
        """Premium users get limits from their plan row."""
        mock_plan = MagicMock()
        mock_plan.download_limit = 100
        mock_plan.max_file_size = 500 * 1024 * 1024
        mock_plan.quality_limit = "4K"

        # First call → Subscription, second → Plan
        mock_db.execute.return_value.scalars.return_value.first.side_effect = [
            MagicMock(),   # subscription exists
            mock_plan,     # plan
        ]

        svc = SubscriptionService(mock_db)
        limits = await svc.check_user_limits(user_id=99)

        assert limits["daily_limit"] == 100
        assert limits["max_file_size"] == 500 * 1024 * 1024
        assert limits["quality_limit"] == "4K"


# ─────────────────────────────────────────────────────────────
# can_user_download
# ─────────────────────────────────────────────────────────────

class TestCanUserDownload:

    @pytest.mark.asyncio
    async def test_user_within_limit_can_download(self, mock_db):
        """User with 2 downloads today (limit=5) should be allowed."""
        # Patch check_user_limits to return limit of 5
        with patch.object(
            SubscriptionService, "check_user_limits",
            new=AsyncMock(return_value={"has_limits": True, "daily_limit": 5}),
        ):
            # Patch today download count = 2
            mock_db.execute.return_value.scalar.return_value = 2

            svc = SubscriptionService(mock_db)
            can, msg = await svc.can_user_download(user_id=1)

        assert can is True
        assert msg == ""

    @pytest.mark.asyncio
    async def test_user_at_limit_cannot_download(self, mock_db):
        """User who has reached daily limit should be blocked."""
        with patch.object(
            SubscriptionService, "check_user_limits",
            new=AsyncMock(return_value={"has_limits": True, "daily_limit": 5}),
        ):
            mock_db.execute.return_value.scalar.return_value = 5  # at limit

            svc = SubscriptionService(mock_db)
            can, msg = await svc.can_user_download(user_id=1)

        assert can is False
        assert "سقف دانلود" in msg

    @pytest.mark.asyncio
    async def test_unlimited_plan_always_allowed(self, mock_db):
        """Users with unlimited plan (has_limits=False) are never blocked."""
        with patch.object(
            SubscriptionService, "check_user_limits",
            new=AsyncMock(return_value={"has_limits": False, "daily_limit": None}),
        ):
            svc = SubscriptionService(mock_db)
            can, msg = await svc.can_user_download(user_id=1)

        assert can is True


# ─────────────────────────────────────────────────────────────
# activate_subscription
# ─────────────────────────────────────────────────────────────

class TestActivateSubscription:

    @pytest.mark.asyncio
    async def test_activate_deactivates_existing(self, mock_db):
        """Activating a new plan deactivates all previous subscriptions."""
        old_sub = MagicMock()
        old_sub.is_active = True

        mock_db.execute.return_value.scalars.return_value.all.return_value = [old_sub]
        mock_db.refresh = AsyncMock()

        svc = SubscriptionService(mock_db)
        await svc.activate_subscription(user_id=1, plan_id=2, duration_days=30)

        assert old_sub.is_active is False
        mock_db.add.assert_called()
        mock_db.commit.assert_awaited()
