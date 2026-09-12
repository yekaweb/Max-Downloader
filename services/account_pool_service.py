"""
Account Pool Service & VIP Tier Management for Crowdsourced Gmail Donors.
"""

import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories.google_account_repo import GoogleAccountRepository
from database.repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)

VIP_TIERS = {
    "sepahbod": {
        "min_accounts": 2,
        "title": "سپهبد (VIP دو ستاره)",
        "daily_limit_gb": 50,
        "max_quality": "4k",
        "priority": 1,
        "badge": "🎖️ سپهبد",
    },
    "esfandiar": {
        "min_accounts": 3,
        "title": "اسفندیار (VIP سه ستاره)",
        "daily_limit_gb": 100,
        "max_quality": "4k_60fps",
        "priority": 2,
        "badge": "⚔️ اسفندیار",
    },
    "rostam": {
        "min_accounts": 5,
        "title": "رستم (اشتراک همیشگی و نامحدود)",
        "daily_limit_gb": 999999,
        "max_quality": "8k",
        "priority": 3,
        "badge": "👑 رستم دستان",
    },
}


class AccountPoolService:
    """
    Manages the Google Account Pool lifecycle, rotation, and VIP donor rewards.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.account_repo = GoogleAccountRepository(db)
        self.user_repo = UserRepository(db)

    def calculate_vip_tier(self, account_count: int) -> Optional[Dict[str, Any]]:
        """Determine VIP tier based on donated accounts count."""
        if account_count >= 5:
            return VIP_TIERS["rostam"]
        elif account_count >= 3:
            return VIP_TIERS["esfandiar"]
        elif account_count >= 2:
            return VIP_TIERS["sepahbod"]
        return None

    async def register_donation(
        self,
        telegram_id: int,
        email: str,
        cookies_json: Optional[str] = None,
        po_token: Optional[str] = None,
        visitor_data: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Process user's Gmail donation, save to pool, and update user VIP status.
        """
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return False, "کاربر در سیستم یافت نشد.", None

        # Clean email
        email = email.strip().lower()
        if "@" not in email or not email.endswith(("@gmail.com", "@googlemail.com")):
            return False, "فرمت ایمیل نامعتبر است. لطفاً یک آدرس Gmail معتبر وارد کنید.", None

        # Save account
        account = await self.account_repo.add_account(
            donor_user_id=user.id,
            email=email,
            cookies_json=cookies_json,
            po_token=po_token,
            visitor_data=visitor_data,
            passkey_registered=True,
        )

        # Recalculate user tier
        total_donations = await self.account_repo.count_donations_by_user(user.id)
        tier_info = self.calculate_vip_tier(total_donations)

        if tier_info:
            user.referral_badge = tier_info["badge"]
            await self.db.commit()

        msg = (
            f"✅ حساب `{email}` با موفقیت در استخر امن افزوده شد.\n"
            f"📊 تعداد کل حساب‌های اهدایی شما: {total_donations}\n"
        )
        if tier_info:
            msg += f"🎉 سطح اشتراک فعال شما: **{tier_info['title']}**"
        else:
            needed = 2 - total_donations
            msg += f"💡 با اهدای {needed} حساب دیگر، به سطح سپهبد (VIP) ارتقا می‌یابید."

        return True, msg, tier_info

    async def get_donor_status(self, telegram_id: int) -> Dict[str, Any]:
        """Get donor statistics and VIP status."""
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return {"donations_count": 0, "tier": None, "accounts": []}

        accounts = await self.account_repo.get_accounts_by_donor(user.id)
        total_count = len(accounts)
        tier_info = self.calculate_vip_tier(total_count)

        return {
            "donations_count": total_count,
            "tier": tier_info,
            "accounts": [{"email": a.email, "status": a.status, "used": a.total_downloads_served} for a in accounts],
        }


__all__ = ["AccountPoolService", "VIP_TIERS"]
