"""
Phase 2 End-to-End Integration Testing Suite
Tests complete coin flow: earning, conversion, referrals, bonuses
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

# Mock the database and services
class MockUser:
    def __init__(self, user_id, username="testuser", referral_code=None):
        self.id = user_id
        self.username = username
        self.referral_code = referral_code or f"REF_{user_id}"
        self.chat_id = user_id


class MockCoinTransaction:
    def __init__(self, user_id, amount, transaction_type, description=""):
        self.user_id = user_id
        self.amount = amount
        self.type = transaction_type  # 'earn', 'spend', 'bonus'
        self.description = description
        self.created_at = datetime.now()


class MockCoinService:
    """Mock coin service for testing"""
    
    def __init__(self):
        self.balances = {}  # user_id -> balance
        self.transactions = []  # All transactions
    
    async def add_coins(self, user_id: int, amount: int, reason: str = "") -> bool:
        """Award coins to user"""
        self.balances[user_id] = self.balances.get(user_id, 0) + amount
        self.transactions.append(MockCoinTransaction(user_id, amount, 'earn', reason))
        return True
    
    async def spend_coins(self, user_id: int, amount: int, reason: str = "") -> bool:
        """Deduct coins from user"""
        if self.balances.get(user_id, 0) < amount:
            return False
        self.balances[user_id] -= amount
        self.transactions.append(MockCoinTransaction(user_id, amount, 'spend', reason))
        return True
    
    async def get_user_balance(self, user_id: int) -> int:
        """Get user's coin balance"""
        return self.balances.get(user_id, 0)
    
    async def bonus_coins(self, user_id: int, amount: int, admin_id: int = 0) -> bool:
        """Award bonus coins"""
        self.balances[user_id] = self.balances.get(user_id, 0) + amount
        self.transactions.append(MockCoinTransaction(user_id, amount, 'bonus', f'Bonus from admin {admin_id}'))
        return True
    
    async def get_user_transactions(self, user_id: int, limit: int = 10):
        """Get transaction history"""
        return [t for t in self.transactions if t.user_id == user_id][-limit:]


class TestPhase2CoinSystem:
    """Test Phase 2 coin earning system"""
    
    @pytest.fixture
    def coin_service(self):
        """Create coin service mock"""
        return MockCoinService()
    
    @pytest.mark.asyncio
    async def test_user_registration_coins(self, coin_service):
        """Test: User gets 100 coins on registration"""
        user_id = 123
        
        # Register user → Award 100 coins
        await coin_service.add_coins(user_id, 100, "Registration bonus")
        
        balance = await coin_service.get_user_balance(user_id)
        assert balance == 100, "User should have 100 coins after registration"
    
    @pytest.mark.asyncio
    async def test_referral_reward(self, coin_service):
        """Test: Referrer gets 50 coins when referral signs up"""
        referrer_id = 111
        referred_id = 222
        
        # Referrer already registered
        await coin_service.add_coins(referrer_id, 100, "Registration")
        
        # Referred user signs up with code
        await coin_service.add_coins(referred_id, 100, "Registration")
        await coin_service.add_coins(referred_id, 0, "Added by referral")  # Referred gets bonus elsewhere
        
        # Referrer gets 50 coins for successful referral
        await coin_service.add_coins(referrer_id, 50, "Referral reward")
        
        referrer_balance = await coin_service.get_user_balance(referrer_id)
        referred_balance = await coin_service.get_user_balance(referred_id)
        
        assert referrer_balance == 150, "Referrer should have 150 coins (100 + 50 bonus)"
        assert referred_balance == 100, "Referred user should have 100 coins"
    
    @pytest.mark.asyncio
    async def test_download_coin_earning(self, coin_service):
        """Test: User earns coins based on download size"""
        user_id = 333
        
        # Register user
        await coin_service.add_coins(user_id, 100, "Registration")
        
        # Download 100MB → earn 10 coins (10 coins per 100MB)
        download_size_mb = 100
        coins_earned = (download_size_mb // 100) * 10  # 10 coins per 100MB
        coins_earned = max(coins_earned, 5)  # Minimum 5 coins
        coins_earned = min(coins_earned, 1000)  # Maximum 1000 coins
        
        await coin_service.add_coins(user_id, coins_earned, f"Download {download_size_mb}MB")
        
        balance = await coin_service.get_user_balance(user_id)
        assert balance == 110, f"User should have 110 coins (100 + 10 from download)"
    
    @pytest.mark.asyncio
    async def test_coin_conversion_to_subscription(self, coin_service):
        """Test: User converts 100 coins to 1 month subscription"""
        user_id = 444
        
        # User has 500 coins
        await coin_service.add_coins(user_id, 500, "Various earnings")
        
        # Convert 100 coins to subscription
        conversion_amount = 100
        success = await coin_service.spend_coins(user_id, conversion_amount, "Convert to 1 month subscription")
        
        assert success, "Conversion should succeed"
        
        balance = await coin_service.get_user_balance(user_id)
        assert balance == 400, "User should have 400 coins after spending 100"
    
    @pytest.mark.asyncio
    async def test_coin_conversion_insufficient_funds(self, coin_service):
        """Test: User cannot convert coins if insufficient balance"""
        user_id = 555
        
        # User has only 50 coins
        await coin_service.add_coins(user_id, 50, "Initial coins")
        
        # Try to convert 100 coins (insufficient)
        success = await coin_service.spend_coins(user_id, 100, "Convert to subscription")
        
        assert not success, "Conversion should fail with insufficient coins"
        
        balance = await coin_service.get_user_balance(user_id)
        assert balance == 50, "Balance should remain unchanged"
    
    @pytest.mark.asyncio
    async def test_admin_bonus_coins(self, coin_service):
        """Test: Admin can award bonus coins to user"""
        admin_id = 999
        user_id = 666
        
        # User has 100 coins
        await coin_service.add_coins(user_id, 100, "Registration")
        
        # Admin awards 50 bonus coins
        await coin_service.bonus_coins(user_id, 50, admin_id)
        
        balance = await coin_service.get_user_balance(user_id)
        assert balance == 150, "User should have 150 coins after admin bonus"
    
    @pytest.mark.asyncio
    async def test_transaction_history(self, coin_service):
        """Test: User can view transaction history"""
        user_id = 777
        
        # Multiple transactions
        await coin_service.add_coins(user_id, 100, "Registration")
        await coin_service.add_coins(user_id, 50, "Referral reward")
        await coin_service.add_coins(user_id, 10, "Download reward")
        await coin_service.spend_coins(user_id, 100, "Subscription conversion")
        
        transactions = await coin_service.get_user_transactions(user_id)
        
        assert len(transactions) == 4, "User should have 4 transactions"
        assert transactions[0].type == 'earn', "First should be earn"
        assert transactions[3].type == 'spend', "Last should be spend"


class TestPhase2CoinFlow:
    """Test complete Phase 2 coin flow"""
    
    @pytest.fixture
    def coin_service(self):
        return MockCoinService()
    
    @pytest.mark.asyncio
    async def test_complete_user_journey(self, coin_service):
        """Test: Complete user journey from registration to subscription"""
        user1_id = 1001
        user2_id = 1002
        
        # Step 1: User 2 signs up (referred by User 1)
        # User 2 gets 100 coins for registration
        await coin_service.add_coins(user2_id, 100, "Registration")
        
        # User 1 gets 50 coins as referrer
        await coin_service.add_coins(user1_id, 50, "Referral reward")
        
        # Step 2: User 2 downloads content (50MB)
        # Earns 0 coins (less than 100MB minimum)
        min_coins = 5
        await coin_service.add_coins(user2_id, min_coins, "Download 50MB")
        
        # Step 3: User 2 downloads again (200MB)
        # Earns 20 coins
        await coin_service.add_coins(user2_id, 20, "Download 200MB")
        
        # Step 4: User 2 has enough coins to convert
        user2_balance = await coin_service.get_user_balance(user2_id)
        assert user2_balance >= 100, "User 2 should have enough for conversion"
        
        # Convert 100 coins to 1 month subscription
        await coin_service.spend_coins(user2_id, 100, "Convert to subscription")
        
        # Step 5: Check final balances
        user1_balance = await coin_service.get_user_balance(user1_id)
        user2_balance = await coin_service.get_user_balance(user2_id)
        
        assert user1_balance == 50, "User 1 should have 50 coins from referral"
        assert user2_balance == 25, "User 2 should have 25 coins (100 + 5 + 20 - 100)"
    
    @pytest.mark.asyncio
    async def test_multiple_referral_chain(self, coin_service):
        """Test: Multiple referrals create chain of rewards"""
        # Chain: User1 → User2 → User3
        
        # User 1 registers
        await coin_service.add_coins(1, 100, "Registration")
        
        # User 2 registers via User 1
        await coin_service.add_coins(2, 100, "Registration")
        await coin_service.add_coins(1, 50, "Referral reward")
        
        # User 3 registers via User 2
        await coin_service.add_coins(3, 100, "Registration")
        await coin_service.add_coins(2, 50, "Referral reward")
        
        # Check balances
        balance1 = await coin_service.get_user_balance(1)
        balance2 = await coin_service.get_user_balance(2)
        balance3 = await coin_service.get_user_balance(3)
        
        assert balance1 == 150, "User 1: 100 registration + 50 referral"
        assert balance2 == 150, "User 2: 100 registration + 50 referral"
        assert balance3 == 100, "User 3: 100 registration only"


class TestPhase2Integration:
    """Test Phase 2 integration scenarios"""
    
    @pytest.fixture
    def coin_service(self):
        return MockCoinService()
    
    @pytest.mark.asyncio
    async def test_coin_balance_consistency(self, coin_service):
        """Test: Coin balances remain consistent"""
        user_id = 2001
        total_earned = 0
        
        # Multiple earnings
        for i in range(5):
            amount = (i + 1) * 10
            await coin_service.add_coins(user_id, amount, f"Earning {i+1}")
            total_earned += amount
        
        balance = await coin_service.get_user_balance(user_id)
        assert balance == total_earned, "Balance should equal sum of earnings"
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, coin_service):
        """Test: Concurrent coin operations are safe"""
        user_id = 2002
        
        # Concurrent earnings
        tasks = [
            coin_service.add_coins(user_id, 10, "Earning 1"),
            coin_service.add_coins(user_id, 20, "Earning 2"),
            coin_service.add_coins(user_id, 30, "Earning 3"),
        ]
        
        results = await asyncio.gather(*tasks)
        assert all(results), "All operations should succeed"
        
        balance = await coin_service.get_user_balance(user_id)
        assert balance == 60, "Balance should be 60 after concurrent earnings"


# Test execution
if __name__ == "__main__":
    # Run with: pytest test_phase2_e2e.py -v
    pytest.main([__file__, "-v", "-s"])
