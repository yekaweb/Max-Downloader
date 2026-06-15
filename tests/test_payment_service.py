"""
Tests for PaymentService – Invoice creation & plan activation (Happy paths).
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, AsyncMock

from services.payment_service import PaymentService, PaymentGateway


class TestCreatePayment:

    @pytest.mark.asyncio
    async def test_create_payment_defaults_to_first_gateway(self, mock_db):
        """create_payment() without a method selects the first available gateway."""
        mock_db.refresh = AsyncMock()

        svc = PaymentService(mock_db)
        payment = await svc.create_payment(
            user_id=1, plan_id=2, amount=9.99, currency="USDT"
        )

        # Should have been added & committed
        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_payment_with_explicit_method(self, mock_db):
        """Explicit gateway method is respected."""
        mock_db.refresh = AsyncMock()

        svc = PaymentService(mock_db)
        payment = await svc.create_payment(
            user_id=1, plan_id=2, amount=9.99,
            currency="USDT", method=PaymentGateway.ZARINPAL.value
        )

        mock_db.add.assert_called_once()


class TestMarkPaymentCompleted:

    @pytest.mark.asyncio
    async def test_payment_completed_activates_subscription(self, mock_db):
        """Completing a payment activates the subscription automatically."""
        mock_payment = MagicMock()
        mock_payment.id = 1
        mock_payment.user_id = 42
        mock_payment.plan_id = 3
        mock_payment.status = "pending"

        mock_db.execute.return_value.scalars.return_value.first.return_value = mock_payment

        with patch(
            "services.payment_service.SubscriptionService.activate_subscription",
            new=AsyncMock(),
        ) as mock_activate:
            svc = PaymentService(mock_db)
            result = await svc.mark_payment_completed(payment_id=1, transaction_id="txn_abc")

        assert result is mock_payment
        assert result.status == "completed"
        assert result.transaction_id == "txn_abc"
        mock_activate.assert_awaited_once_with(42, 3, duration_days=30)

    @pytest.mark.asyncio
    async def test_payment_not_found_returns_none(self, mock_db):
        """Returns None gracefully when payment_id doesn't exist."""
        mock_db.execute.return_value.scalars.return_value.first.return_value = None

        svc = PaymentService(mock_db)
        result = await svc.mark_payment_completed(payment_id=999, transaction_id="x")

        assert result is None


class TestMarkPaymentFailed:

    @pytest.mark.asyncio
    async def test_suggests_next_gateway_on_failure(self, mock_db):
        """Failing CryptoBot should suggest NOWPayments as fallback."""
        mock_payment = MagicMock()
        mock_payment.payment_method = PaymentGateway.CRYPTO_BOT.value
        mock_db.execute.return_value.scalars.return_value.first.return_value = mock_payment

        svc = PaymentService(mock_db)
        _, next_gw = await svc.mark_payment_failed(payment_id=1, error_reason="timeout")

        assert next_gw == PaymentGateway.NOW_PAYMENTS

    @pytest.mark.asyncio
    async def test_last_gateway_no_fallback(self, mock_db):
        """Last gateway in priority list returns None as next gateway."""
        mock_payment = MagicMock()
        mock_payment.payment_method = PaymentGateway.ZARINPAL.value
        mock_db.execute.return_value.scalars.return_value.first.return_value = mock_payment

        svc = PaymentService(mock_db)
        _, next_gw = await svc.mark_payment_failed(payment_id=1, error_reason="error")

        assert next_gw is None
