"""Coin transaction service - manage user coins and transactions"""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database.models import CoinTransaction, User


class CoinTransactionService:
    """Service for managing coin transactions and user coin balance"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def add_coins(
        self,
        user_id: int,
        amount: float,
        transaction_type: str = "earn",
        description: str = None
    ) -> CoinTransaction:
        """
        Add coins to user's balance and create transaction record.
        
        Args:
            user_id: User database ID
            amount: Coins to add (can be negative for spending)
            transaction_type: Type of transaction (earn, spend, referral, bonus, etc.)
            description: Optional description of the transaction
        
        Returns:
            CoinTransaction object
        """
        transaction = CoinTransaction(
            user_id=user_id,
            amount=amount,
            transaction_type=transaction_type,
            description=description or f"{transaction_type.capitalize()} transaction"
        )
        self.db.add(transaction)
        
        # Update user's total coins
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if user:
            user.total_coins = max(0, user.total_coins + amount)  # Prevent negative balance
            self.db.add(user)
        
        await self.db.commit()
        return transaction
    
    async def get_user_balance(self, user_id: int) -> float:
        """Get user's current coin balance"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        return user.total_coins if user else 0.0
    
    async def get_user_transactions(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> list[CoinTransaction]:
        """Get user's transaction history"""
        result = await self.db.execute(
            select(CoinTransaction)
            .where(CoinTransaction.user_id == user_id)
            .order_by(CoinTransaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_transaction_stats(self, user_id: int) -> dict:
        """Get coin transaction statistics for user"""
        result = await self.db.execute(
            select(
                func.count(CoinTransaction.id).label("total_transactions"),
                func.sum(CoinTransaction.amount).label("total_earned"),
            ).where(
                CoinTransaction.user_id == user_id,
                CoinTransaction.amount > 0
            )
        )
        row = result.first()
        
        spend_result = await self.db.execute(
            select(
                func.sum(CoinTransaction.amount).label("total_spent"),
            ).where(
                CoinTransaction.user_id == user_id,
                CoinTransaction.amount < 0
            )
        )
        spend_row = spend_result.first()
        
        return {
            "total_transactions": row[0] or 0,
            "total_earned": row[1] or 0.0,
            "total_spent": abs(spend_row[0]) if spend_row[0] else 0.0,
        }
    
    async def spend_coins(
        self,
        user_id: int,
        amount: float,
        description: str = "Subscription purchase"
    ) -> tuple[bool, str, CoinTransaction]:
        """
        Spend coins from user's balance.
        
        Returns:
            (success, message, transaction)
        """
        # Check balance
        balance = await self.get_user_balance(user_id)
        if balance < amount:
            return False, f"Insufficient coins. You have {balance:.0f}, need {amount:.0f}", None
        
        # Deduct coins
        transaction = await self.add_coins(
            user_id=user_id,
            amount=-amount,
            transaction_type="spend",
            description=description
        )
        
        return True, f"Successfully spent {amount:.0f} coins", transaction
    
    async def bonus_coins(
        self,
        user_id: int,
        amount: float,
        reason: str = "Admin bonus"
    ) -> CoinTransaction:
        """Add bonus coins to user (admin action)"""
        return await self.add_coins(
            user_id=user_id,
            amount=amount,
            transaction_type="bonus",
            description=reason
        )


__all__ = ["CoinTransactionService"]
