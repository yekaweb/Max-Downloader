"""Payment service with gateway fallback strategy"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Payment
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple
from loguru import logger
from utils.db_utils import scalars_first
from services.subscription_service import SubscriptionService


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
        payment = await scalars_first(result)
        
        if payment:
            payment.status = "completed"
            payment.transaction_id = transaction_id
            payment.completed_at = datetime.now()
            
            # Activate the plan!
            from services.subscription_service import SubscriptionService
            sub_service = SubscriptionService(self.db)
            await sub_service.activate_subscription(payment.user_id, payment.plan_id, duration_days=30)
            
            await self.db.commit()
            
            logger.info(f"Payment {payment_id} marked as completed (txn: {transaction_id}) and plan {payment.plan_id} activated")
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
        payment = await scalars_first(result)
        
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
                
                if gateway == PaymentGateway.CRYPTO_BOT:
                    invoice_url = await self._create_cryptobot_invoice(payment)
                elif gateway == PaymentGateway.ZARINPAL:
                    invoice_url = await self._create_zarinpal_invoice(payment)
                elif gateway == PaymentGateway.NOW_PAYMENTS:
                    invoice_url = await self._create_nowpayments_invoice(payment)
                else:
                    # Fallback for others for now
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

    async def _create_cryptobot_invoice(self, payment: Payment) -> str:
        """Create invoice via Telegram CryptoBot API"""
        from config import settings
        import aiohttp
        
        if not settings.CRYPTOPAY_TOKEN:
            raise ValueError("CRYPTOPAY_TOKEN is not configured")
            
        url = "https://pay.crypt.bot/api/createInvoice"
        headers = {
            "Crypto-Pay-API-Token": settings.CRYPTOPAY_TOKEN
        }
        payload = {
            "asset": payment.currency if payment.currency in ["USDT", "TON", "BTC", "ETH", "LTC", "BNB", "TRX", "USDC"] else "USDT",
            "amount": str(payment.amount),
            "description": f"Subscription Plan for user {payment.user_id}",
            "payload": f"payment_{payment.id}",
            "expires_in": 3600  # 1 hour
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                result = await response.json()
                if result.get("ok"):
                    return result["result"]["pay_url"]
                else:
                    error_msg = result.get("error", {}).get("name", "Unknown error")
                    raise Exception(f"CryptoBot API error: {error_msg}")

    async def _create_zarinpal_invoice(self, payment: Payment) -> str:
        """Create invoice via ZarinPal API (IRR)"""
        from config import settings
        import aiohttp
        
        if not settings.ZARINPAL_MERCHANT:
            raise ValueError("ZARINPAL_MERCHANT is not configured")
            
        url = "https://api.zarinpal.com/pg/v4/payment/request.json"
        headers = {
            "accept": "application/json", 
            "content-type": "application/json"
        }
        
        # Assuming WEB_HOST is an external accessible URL for the callback
        callback_url = f"http://{settings.WEB_HOST}:{settings.WEB_PORT}/payment/verify/zarinpal?payment_id={payment.id}"
        
        payload = {
            "merchant_id": settings.ZARINPAL_MERCHANT,
            "amount": int(payment.amount), # amount should be in IRR or Toman based on ZarinPal config
            "callback_url": callback_url,
            "description": f"Subscription Plan for user {payment.user_id}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                result = await response.json()
                data = result.get("data", {})
                if data and data.get("code") == 100:
                    authority = data.get("authority")
                    return f"https://www.zarinpal.com/pg/StartPay/{authority}"
                else:
                    error_msg = result.get("errors", {}).get("message", "Unknown error")
                    raise Exception(f"ZarinPal API error: {error_msg}")

    async def _create_nowpayments_invoice(self, payment: Payment) -> str:
        """Create invoice via NOWPayments API"""
        from config import settings
        import aiohttp
        
        if not settings.NOWPAYMENTS_KEY:
            raise ValueError("NOWPAYMENTS_KEY is not configured")
            
        url = "https://api.nowpayments.io/v1/invoice"
        headers = {
            "x-api-key": settings.NOWPAYMENTS_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "price_amount": payment.amount,
            "price_currency": payment.currency,
            "order_id": str(payment.id),
            "order_description": f"Subscription Plan for user {payment.user_id}",
            "ipn_callback_url": f"http://{settings.WEB_HOST}:{settings.WEB_PORT}/payment/verify/nowpayments",
            "success_url": "https://t.me/dlbot",
            "cancel_url": "https://t.me/dlbot"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                result = await response.json()
                if "invoice_url" in result:
                    return result["invoice_url"]
                else:
                    error_msg = result.get("message", "Unknown error")
                    raise Exception(f"NOWPayments API error: {error_msg}")

__all__ = ["PaymentService", "PaymentGateway"]

