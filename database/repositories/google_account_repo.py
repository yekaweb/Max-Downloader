"""
Repository for Google Account Pool management.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.google_account_pool import GoogleAccount


class GoogleAccountRepository:
    """
    CRUD and operational queries for crowdsourced Google accounts.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_account(
        self,
        donor_user_id: int,
        email: str,
        cookies_json: Optional[str] = None,
        po_token: Optional[str] = None,
        visitor_data: Optional[str] = None,
        passkey_registered: bool = True,
    ) -> GoogleAccount:
        """Register a new donated Google account."""
        # Check if already exists
        existing = await self.get_by_email(email)
        if existing:
            existing.donor_user_id = donor_user_id
            existing.passkey_registered = passkey_registered
            if cookies_json:
                existing.cookies_json = cookies_json
            if po_token:
                existing.po_token = po_token
            if visitor_data:
                existing.visitor_data = visitor_data
            existing.status = "active"
            existing.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        account = GoogleAccount(
            donor_user_id=donor_user_id,
            email=email,
            cookies_json=cookies_json,
            po_token=po_token,
            visitor_data=visitor_data,
            passkey_registered=passkey_registered,
            status="active",
        )
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def get_by_email(self, email: str) -> Optional[GoogleAccount]:
        """Fetch account by email."""
        result = await self.session.execute(
            select(GoogleAccount).where(GoogleAccount.email == email)
        )
        return result.scalars().first()

    async def get_accounts_by_donor(self, donor_user_id: int) -> List[GoogleAccount]:
        """Fetch all accounts donated by a specific user."""
        result = await self.session.execute(
            select(GoogleAccount).where(GoogleAccount.donor_user_id == donor_user_id)
        )
        return list(result.scalars().all())

    async def count_donations_by_user(self, donor_user_id: int) -> int:
        """Count total active accounts donated by a user."""
        result = await self.session.execute(
            select(func.count(GoogleAccount.id)).where(
                GoogleAccount.donor_user_id == donor_user_id,
                GoogleAccount.status.in_(["active", "warming_up", "refresh_needed"])
            )
        )
        return result.scalar() or 0

    async def get_active_accounts(self) -> List[GoogleAccount]:
        """Fetch all active accounts ready for rotation."""
        result = await self.session.execute(
            select(GoogleAccount).where(GoogleAccount.status == "active")
        )
        return list(result.scalars().all())

    async def get_least_used_account(self) -> Optional[GoogleAccount]:
        """Get the account with the lowest daily usage for optimal load balancing."""
        result = await self.session.execute(
            select(GoogleAccount)
            .where(GoogleAccount.status == "active")
            .order_by(GoogleAccount.daily_downloads_count.asc(), GoogleAccount.last_used_at.asc())
        )
        return result.scalars().first()

    async def record_usage(self, account_id: int):
        """Increment download counter and update last_used_at."""
        await self.session.execute(
            update(GoogleAccount)
            .where(GoogleAccount.id == account_id)
            .values(
                total_downloads_served=GoogleAccount.total_downloads_served + 1,
                daily_downloads_count=GoogleAccount.daily_downloads_count + 1,
                last_used_at=datetime.utcnow()
            )
        )
        await self.session.commit()

    async def update_session_data(
        self,
        account_id: int,
        cookies_json: Optional[str] = None,
        po_token: Optional[str] = None,
        visitor_data: Optional[str] = None,
        status: str = "active",
    ):
        """Update refreshed session cookies, PO-Token, and status."""
        values = {
            "status": status,
            "last_refreshed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        if cookies_json is not None:
            values["cookies_json"] = cookies_json
        if po_token is not None:
            values["po_token"] = po_token
        if visitor_data is not None:
            values["visitor_data"] = visitor_data

        await self.session.execute(
            update(GoogleAccount).where(GoogleAccount.id == account_id).values(**values)
        )
        await self.session.commit()


__all__ = ["GoogleAccountRepository"]
