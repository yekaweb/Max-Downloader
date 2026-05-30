"""Payment service with gateway fallback strategy"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Payment
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple
from loguru import logger


class PaymentGateway(str, Enum):
    """Available payment gateways with priority order"""
    CRYPTO_BOT = "cryptobot"      # Priority 1: CryptoBot (Telegram native)
    NOW_PAYMENTS = "nowpayments"  # Priority 2: NOWPayments (Crypto)
    ZARINPAL = "zarinpal"         # Priority 3: ZarinPal (Persian/Iranian)


class PaymentService:
    """Payment service with fallback strategy"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
        # Gateway priority order - tried in sequence if previous fails
        self.GATEWAY_PRIORITY = [
            PaymentGateway.CRYPTO_BOT,    # Try CryptoBot first (best for international)
            PaymentGateway.NOW_PAYMENTS,  # Fallback to NOWPayments
            PaymentGateway.ZARINPAL,      # Last resort: ZarinPal (Iran-specific)
        ]
        
        # Gateway availability configuration
        self.enabled_gateways = {
            PaymentGateway.CRYPTO_BOT: True,      # Usually available
            PaymentGateway.NOW_PAYMENTS: True,    # Usually available
            PaymentGateway.ZARINPAL: True,        # Available in Iran
        }

    def get_available_gateways(self) -> list[PaymentGateway]:
        """
        Get available payment gateways in priority order.
        
        Returns:
            List of available gateways sorted by priority (highest first)
        """
        return [
            gw for gw in self.GATEWAY_PRIORITY
            if self.enabled_gateways.get(gw, False)
        ]
    
    async def create_payment(
        self,
        user_id: int,
        plan_id: int,
        amount: float,
        currency: str = "USD",
        method: str = None
    ) -> Payment:
        """
        Create a payment record with default or specified gateway.
        
        Args:
            user_id: User making payment
            plan_id: Plan being purchased
            amount: Amount to charge
            currency: Currency code (default USD)
            method: Specific gateway (if None, will select first available)
        
        Returns:
            Payment record
        """
        if not method:
            # Auto-select first available gateway
            available = self.get_available_gateways()
            method = available[0].value if available else PaymentGateway.CRYPTO_BOT.value
        
        payment = Payment(
            user_id=user_id,
            plan_id=plan_id,
            amount=amount,
            currency=currency,
            payment_method=method,
            status="pending"
        )
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        
        logger.info(f"Created payment {payment.id} for user {user_id} using {method}")
        return payment

    async def mark_payment_completed(
        self,
        payment_id: int,
        transaction_id: str
    ) -> Optional[Payment]:
        """
        Mark a payment as completed.
        
        Args:
            payment_id: ID of payment to mark complete
            transaction_id: External transaction ID from gateway
        
        Returns:
            Updated Payment record or None if not found
        """
        result = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        payment = result.scalars().first()
        
        if payment:
            payment.status = "completed"
            payment.transaction_id = transaction_id
            payment.completed_at = datetime.now()
            await self.db.commit()
            
            logger.info(f"Payment {payment_id} marked as completed (txn: {transaction_id})")
            return payment
        
        logger.warning(f"Payment {payment_id} not found for completion")
        return None

    async def mark_payment_failed(
        self,
        payment_id: int,
        error_reason: str = None,
        fallback_gateway: Optional[PaymentGateway] = None
    ) -> Tuple[Optional[Payment], Optional[PaymentGateway]]:
        """
        Mark payment as failed and optionally suggest fallback gateway.
        
        Args:
            payment_id: Payment ID that failed
            error_reason: Reason for failure
            fallback_gateway: Gateway to suggest for retry
        
        Returns:
            (Updated payment, suggested fallback gateway)
        """
        result = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        payment = result.scalars().first()
        
        if not payment:
            logger.warning(f"Payment {payment_id} not found for failure marking")
            return None, None
        
        # Try to find next gateway in priority list
        current_gateway = PaymentGateway(payment.payment_method)
        current_index = self.GATEWAY_PRIORITY.index(current_gateway)
        next_gateway = None
        
        if current_index < len(self.GATEWAY_PRIORITY) - 1:
            next_gateway = self.GATEWAY_PRIORITY[current_index + 1]
        
        payment.status = "failed"
        payment.error_message = error_reason or "Unknown error"
        await self.db.commit()
        
        logger.warning(f"Payment {payment_id} failed: {error_reason}")
        if next_gateway:
            logger.info(f"Suggesting fallback gateway: {next_gateway.value}")
        
        return payment, next_gateway

    async def create_invoice_with_fallback(
        self,
        user_id: int,
        plan_id: int,
        amount: float,
        currency: str = "USDT"
    ) -> Tuple[Optional[str], Optional[PaymentGateway]]:
        """
        Create invoice with automatic fallback to next gateway if primary fails.
        
        Args:
            user_id: User ID
            plan_id: Plan ID
            amount: Amount to charge
            currency: Currency code
        
        Returns:
            (Invoice URL, Gateway used)
        """
        available_gateways = self.get_available_gateways()
        last_error = None
        
        for gateway in available_gateways:
            try:
                # Create payment record
                payment = await self.create_payment(
                    user_id=user_id,
                    plan_id=plan_id,
                    amount=amount,
                    currency=currency,
                    method=gateway.value
                )
                
                # TODO: Call actual gateway API to create invoice
                # invoice_url = await self._create_gateway_invoice(gateway, payment)
                invoice_url = f"https://payment.example.com/{payment.id}"
                
                logger.info(f"Successfully created invoice via {gateway.value}")
                return invoice_url, gateway
                
            except Exception as e:
                last_error = e
                logger.warning(f"Failed to create invoice via {gateway.value}: {e}")
                continue
        
        # All gateways failed
        logger.error(f"All payment gateways failed. Last error: {last_error}")
        return None, None


__all__ = ["PaymentService", "PaymentGateway"]

