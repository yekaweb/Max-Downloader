"""Coins statistics API routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta
from database.models import CoinTransaction, User, Referral
from database.connection import AsyncSessionLocal

router = APIRouter(prefix="/api/coins", tags=["coins"])


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/statistics")
async def get_coin_statistics(session: AsyncSession = Depends(get_db)):
    """Get overall coin system statistics"""
    try:
        # Total coins earned
        total_coins_result = await session.execute(
            select(func.sum(CoinTransaction.amount)).where(
                CoinTransaction.amount > 0
            )
        )
        total_coins = total_coins_result.scalar() or 0
        
        # Total coins spent
        total_spent_result = await session.execute(
            select(func.sum(CoinTransaction.amount)).where(
                CoinTransaction.amount < 0
            )
        )
        total_spent = abs(total_spent_result.scalar() or 0)
        
        # Coins today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_coins_result = await session.execute(
            select(func.sum(CoinTransaction.amount)).where(
                CoinTransaction.amount > 0,
                CoinTransaction.created_at >= today_start
            )
        )
        today_coins = today_coins_result.scalar() or 0
        
        # Total transactions
        tx_count_result = await session.execute(
            select(func.count(CoinTransaction.id))
        )
        total_transactions = tx_count_result.scalar() or 0
        
        # Active users with coins
        active_users_result = await session.execute(
            select(func.count(func.distinct(CoinTransaction.user_id)))
        )
        active_users = active_users_result.scalar() or 0
        
        return {
            "total_coins": float(total_coins),
            "total_spent": float(total_spent),
            "coins_today": float(today_coins),
            "total_transactions": total_transactions,
            "active_users": active_users,
            "net_coins": float(total_coins - total_spent)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard")
async def get_coin_leaderboard(
    limit: int = 10,
    days: int = 7,
    session: AsyncSession = Depends(get_db)
):
    """Get top coin earners in the last N days"""
    try:
        date_from = datetime.utcnow() - timedelta(days=days)
        
        # Get top earners
        result = await session.execute(
            select(
                User.id,
                User.first_name,
                User.last_name,
                User.telegram_id,
                func.sum(CoinTransaction.amount).label("total_coins")
            )
            .join(CoinTransaction)
            .where(
                CoinTransaction.amount > 0,
                CoinTransaction.created_at >= date_from
            )
            .group_by(User.id)
            .order_by(desc("total_coins"))
            .limit(limit)
        )
        
        leaderboard = []
        for row in result:
            leaderboard.append({
                "user_id": row.id,
                "telegram_id": row.telegram_id,
                "name": f"{row.first_name} {row.last_name or ''}".strip(),
                "coins": float(row.total_coins)
            })
        
        return leaderboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions")
async def get_all_transactions(
    page: int = 1,
    limit: int = 50,
    session: AsyncSession = Depends(get_db)
):
    """Get all coin transactions with pagination"""
    try:
        offset = (page - 1) * limit
        
        # Get total count
        count_result = await session.execute(
            select(func.count(CoinTransaction.id))
        )
        total = count_result.scalar() or 0
        
        # Get transactions
        result = await session.execute(
            select(CoinTransaction)
            .order_by(desc(CoinTransaction.created_at))
            .offset(offset)
            .limit(limit)
        )
        
        transactions = []
        for tx in result.scalars():
            user = await session.get(User, tx.user_id)
            transactions.append({
                "id": tx.id,
                "user_id": tx.user_id,
                "user_name": f"{user.first_name} {user.last_name or ''}".strip() if user else "Unknown",
                "amount": float(tx.amount),
                "type": tx.transaction_type,
                "description": tx.description,
                "created_at": tx.created_at.isoformat()
            })
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
            "transactions": transactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}")
async def get_user_coin_stats(
    user_id: int,
    session: AsyncSession = Depends(get_db)
):
    """Get coin statistics for a specific user"""
    try:
        # Get user
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Total earned
        earned_result = await session.execute(
            select(func.sum(CoinTransaction.amount)).where(
                CoinTransaction.user_id == user_id,
                CoinTransaction.amount > 0
            )
        )
        total_earned = earned_result.scalar() or 0
        
        # Total spent
        spent_result = await session.execute(
            select(func.sum(CoinTransaction.amount)).where(
                CoinTransaction.user_id == user_id,
                CoinTransaction.amount < 0
            )
        )
        total_spent = abs(spent_result.scalar() or 0)
        
        # Transaction count
        tx_count_result = await session.execute(
            select(func.count(CoinTransaction.id)).where(
                CoinTransaction.user_id == user_id
            )
        )
        transaction_count = tx_count_result.scalar() or 0
        
        # Referral count
        ref_count_result = await session.execute(
            select(func.count(Referral.id)).where(
                Referral.referrer_id == user_id,
                Referral.status == "completed"
            )
        )
        referral_count = ref_count_result.scalar() or 0
        
        return {
            "user_id": user.id,
            "telegram_id": user.telegram_id,
            "name": f"{user.first_name} {user.last_name or ''}".strip(),
            "current_balance": float(user.total_coins),
            "total_earned": float(total_earned),
            "total_spent": float(total_spent),
            "transaction_count": transaction_count,
            "referral_count": referral_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending_transactions(
    limit: int = 20,
    session: AsyncSession = Depends(get_db)
):
    """Get trending transactions for dashboard"""
    try:
        result = await session.execute(
            select(CoinTransaction)
            .order_by(desc(CoinTransaction.created_at))
            .limit(limit)
        )
        
        transactions = []
        for tx in result.scalars():
            user = await session.get(User, tx.user_id)
            transactions.append({
                "id": tx.id,
                "user_name": f"{user.first_name}" if user else "Unknown",
                "amount": float(tx.amount),
                "type": tx.transaction_type,
                "description": tx.description,
                "created_at": tx.created_at.isoformat()
            })
        
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
