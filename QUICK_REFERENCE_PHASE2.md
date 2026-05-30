# 🚀 Phase 2 Quick Reference - What's Ready to Use

**Status**: Ready for immediate integration and testing  
**Completion**: 30% (Progress Bar ✅ + Coin System 70% Ready - Service Layer Complete ✅)

---

## 📌 NEW BOT COMMANDS

### User Commands

```
/referral
├── Shows: Your referral code, completed referrals, earned coins
├── Actions: Share referral code
└── Updates: Auto-generates code if missing

/coins
├── Shows: Current balance, earned/spent totals, transaction history
├── Actions: View last 10 transactions
└── UI: Quick access to conversion

/convert_coins
├── Purpose: Convert coins to subscription months
├── Input: Select plan and duration
├── Actions: Deducts coins → Creates subscription
└── Safety: Checks balance before conversion
```

---

## 📊 NEW SERVICES

### CoinTransactionService
**Location**: `services/coin_service.py`

```python
from services import CoinTransactionService

# Create instance
coin_service = CoinTransactionService(db_session)

# Award coins (for download, referral, etc.)
await coin_service.add_coins(
    user_id=123,
    amount=50.0,
    transaction_type="referral",
    description="Referred user joined"
)

# Spend coins (for subscription conversion)
success, msg, tx = await coin_service.spend_coins(
    user_id=123,
    amount=100.0,
    description="Converted to Premium"
)

# Get balance
balance = await coin_service.get_user_balance(user_id=123)

# Get history
transactions = await coin_service.get_user_transactions(user_id=123, limit=10)

# Get stats
stats = await coin_service.get_transaction_stats(user_id=123)
# Returns: {total_transactions, total_earned, total_spent}
```

### Enhanced ReferralService
**Location**: `services/referral_service.py`

```python
from services import ReferralService

ref_service = ReferralService(db_session)

# Validate referral code
is_valid, msg, referrer = await ref_service.is_referral_valid(
    referral_code="ABC12345",
    current_user_id=456
)

# Create referral
referral = await ref_service.create_referral(
    referrer_id=123,
    referred_user_id=456
)

# Complete referral (awards coins)
success, msg = await ref_service.mark_referral_complete(
    referral_id=referral.id
)

# Get referral stats
count = await ref_service.get_user_referral_count(user_id=123)
```

---

## 💎 COIN CONFIGURATION

### Current Rates
```
Signup Bonus:    100 coins (new user)
Referrer Bonus:   50 coins (for each referral)
Conversion Rate: 100 coins = 1 month Premium

### Download Earning: (Ready to integrate - see COIN_EARNING_INTEGRATION_GUIDE.md)
- 10 coins per 100 MB ✅ Configured
- Min: 5 coins, Max: 1000 coins ✅ Configured
- Integration: Hook into download completion handler
```

### Earning Examples
```
25 MB download  →  5 coins (minimum)
100 MB download → 10 coins
250 MB download → 25 coins
1 GB download   → 100 coins
1.5 GB download → 150 coins
```

---

## 🔌 INTEGRATION POINTS (Todo)

### 1. Download Completion
**File**: `bot/handlers/download.py`  
**When**: After file successfully uploaded to user  
**Code**:
```python
coin_service = CoinTransactionService(session)
file_size_mb = downloaded_size_bytes / (1024 * 1024)
coins = int(file_size_mb / 100 * 10)
coins = max(5, min(coins, 1000))

await coin_service.add_coins(
    user_id=user.id,
    amount=coins,
    transaction_type="download",
    description=f"Downloaded {file_size_mb:.1f} MB"
)
```

### 2. Referral Signup
**File**: `bot/handlers/start.py`  
**When**: After user registration  
**Code**:
```python
referral_code = message.text.split()[-1] if len(message.text.split()) > 1 else None

ref_service = ReferralService(session)
is_valid, msg, referrer = await ref_service.is_referral_valid(
    referral_code,
    current_user_id=user.id
)

if is_valid:
    referral = await ref_service.create_referral(
        referrer_id=referrer.id,
        referred_user_id=user.id
    )
    await ref_service.mark_referral_complete(referral.id)
```

### 3. Admin Bonus Coins
**File**: Create `bot/handlers/admin/bonus_coins.py`  
**Command**: `/admin_bonus <user_id> <amount> [reason]`

---

## 📁 NEW & MODIFIED FILES

### New Source Files
1. ✅ `services/coin_service.py` - Coin transaction service (157 lines)
2. ✅ `bot/handlers/coin_conversion.py` - Coin conversion flow (175 lines)
3. ✅ `test_progress_verification.py` - Progress bar tests (270 lines)

### Enhanced Files
1. ✅ `services/referral_service.py` - Added coin rewards logic
2. ✅ `bot/handlers/referral.py` - Added `/coins` command
3. ✅ `services/__init__.py` - Export CoinTransactionService
4. ✅ `ROADMAP.md` - Updated Phase 2 to 30%
5. ✅ `README.md` - Updated Phase 2 status with detailed checkmarks

### Documentation (✅ Complete)
1. ✅ `PHASE_2_PROGRESS_REPORT.md` - Updated with 70% completion details
2. ✅ `COIN_EARNING_INTEGRATION_GUIDE.md` - Integration examples provided
3. ✅ `SESSION_SUMMARY.md` - Session overview
4. ✅ `QUICK_REFERENCE_PHASE2.md` - This file (updated)
5. ✅ `IMPLEMENTATION_CHECKLIST.md` - Verification checklist
6. ✅ `FILE_INDEX.md` - Complete file structure

---

## ✅ WHAT'S WORKING NOW

- ✅ `/referral` command - Show code and stats
- ✅ `/coins` command - Show balance and history
- ✅ `/convert_coins` command - Convert to subscription
- ✅ Coin balance tracking
- ✅ Transaction history
- ✅ Referral code validation
- ✅ Coin-to-subscription conversion with database creation
- ✅ Progress bar with throttling
- ✅ Auto-update progress messages (max 1 per 3 seconds)

---

## ⏳ NOT YET INTEGRATED (Ready for Integration)

- ⏳ Download coin earning (5-10 min integration time - waiting for completion handler hook)
- ⏳ Referral signup automation (5-10 min - needs /start command hook)
- ⏳ Admin bonus coins command (10-15 min - new /admin_bonus command)
- ⏳ Referral signup flow (needs `/start` integration)
- ⏳ Admin bonus coins command
- ⏳ Payment system integration
- ⏳ Subscription expiration checks

---

## 🧪 QUICK TEST

### Test Coin Earning
```python
# In Python console or test file
import asyncio
from services import CoinTransactionService
from database.connection import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as session:
        service = CoinTransactionService(session)
        
        # Add coins
        tx = await service.add_coins(
            user_id=1,
            amount=100,
            transaction_type="test"
        )
        print(f"✅ Added: {tx}")
        
        # Check balance
        balance = await service.get_user_balance(user_id=1)
        print(f"✅ Balance: {balance}")
        
        # Spend coins
        success, msg, tx = await service.spend_coins(
            user_id=1,
            amount=50
        )
        print(f"✅ {msg}")

asyncio.run(test())
```

### Test Referral
```python
# Test referral validation
async def test():
    async with AsyncSessionLocal() as session:
        ref_service = ReferralService(session)
        
        is_valid, msg, referrer = await ref_service.is_referral_valid(
            "ABC123456",  # Your referral code
            current_user_id=999  # Test user
        )
        print(f"Valid: {is_valid}, Message: {msg}")
        if is_valid:
            print(f"Referrer: {referrer.first_name}")

asyncio.run(test())
```

---

## 🎯 NEXT SESSION PRIORITIES

**High Priority** (30-45 min):
1. Integrate download coin earning
2. Integrate referral signup flow
3. Complete end-to-end testing

**Medium Priority** (1-2 hours):
4. Admin bonus coins command
5. Web panel coin dashboard

**Lower Priority** (Later tasks):
6. CryptoBot payment integration
7. Other Phase 2 components

---

## 📞 Questions & Notes

### What's the conversion rate?
100 coins = 1 month of Premium subscription

### How do users get coins?
- Signup via referral: 100 coins
- Refer someone: 50 coins per successful referral
- Download files: 10 coins per 100 MB (not yet integrated)

### Can coins be refunded?
Not yet - current implementation doesn't support refunds.

### How does referral signup work?
Send user a deeplink with `/start <referral_code>` parameter

### What about expiring subscriptions?
Need to add scheduled task to check/notify expiring subscriptions

---

*Quick Reference Generated: 2026-05-23*  
*For detailed info, see: PHASE_2_PROGRESS_REPORT.md*
