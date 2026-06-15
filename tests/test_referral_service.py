"""
Tests for ReferralService – milestone rewards (Happy paths).
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.referral_service import ReferralService


class TestReferralCompletion:

    @pytest.mark.asyncio
    async def test_complete_referral_awards_coins(self, mock_db):
        """Both referrer and referred user receive coins."""
        mock_referral = MagicMock()
        mock_referral.status = "pending"
        mock_referral.referrer_id = 1
        mock_referral.referred_user_id = 2
        mock_referral.reward_coins = 0

        mock_referrer = MagicMock()
        mock_referrer.id = 1
        mock_referrer.total_coins = 100.0
        mock_referrer.referral_count = 0
        mock_referrer.referral_milestone = 0

        mock_referred = MagicMock()
        mock_referred.id = 2
        mock_referred.total_coins = 0.0

        # execute() called 3 times: referral, referrer user, referred user
        mock_db.execute.return_value.scalars.return_value.first.side_effect = [
            mock_referral,
            mock_referrer,
            mock_referred,
        ]

        svc = ReferralService(mock_db)
        success, msg = await svc.mark_referral_complete(referral_id=1)

        assert success is True
        assert mock_referral.status == "completed"
        assert mock_referrer.total_coins > 100.0   # coins added
        assert mock_referred.total_coins > 0.0

    @pytest.mark.asyncio
    async def test_referral_not_found_returns_false(self, mock_db):
        mock_db.execute.return_value.scalars.return_value.first.return_value = None

        svc = ReferralService(mock_db)
        success, msg = await svc.mark_referral_complete(referral_id=999)

        assert success is False
        assert "not found" in msg

    @pytest.mark.asyncio
    async def test_already_completed_referral_rejected(self, mock_db):
        mock_referral = MagicMock()
        mock_referral.status = "completed"
        mock_db.execute.return_value.scalars.return_value.first.return_value = mock_referral

        svc = ReferralService(mock_db)
        success, msg = await svc.mark_referral_complete(referral_id=1)

        assert success is False
        assert "already completed" in msg


class TestReferralValidation:

    @pytest.mark.asyncio
    async def test_valid_referral_code(self, mock_db):
        mock_referrer = MagicMock()
        mock_referrer.id = 10
        mock_db.execute.return_value.scalars.return_value.first.return_value = mock_referrer

        svc = ReferralService(mock_db)
        is_valid, msg, user = await svc.is_referral_valid("ABCDE12345", current_user_id=99)

        assert is_valid is True
        assert user is mock_referrer

    @pytest.mark.asyncio
    async def test_cannot_use_own_referral_code(self, mock_db):
        mock_referrer = MagicMock()
        mock_referrer.id = 42   # same as current user
        mock_db.execute.return_value.scalars.return_value.first.return_value = mock_referrer

        svc = ReferralService(mock_db)
        is_valid, msg, user = await svc.is_referral_valid("ABCDE12345", current_user_id=42)

        assert is_valid is False
        assert "own" in msg

    @pytest.mark.asyncio
    async def test_short_code_invalid(self, mock_db):
        svc = ReferralService(mock_db)
        is_valid, msg, user = await svc.is_referral_valid("AB", current_user_id=1)

        assert is_valid is False
        assert user is None
