"""Unit tests for database models"""
import pytest
from database.models.models import User, CachedFile, Payment, Referral


@pytest.mark.unit
class TestUserModel:
    """Test User model"""
    
    async def test_user_creation(self, db_session, mock_user_data):
        """Test creating a user"""
        user = User(**mock_user_data)
        db_session.add(user)
        await db_session.commit()
        
        assert user.id is not None
        assert user.telegram_id == mock_user_data["telegram_id"]
        assert user.referral_count == 0
        assert user.referral_milestone == 0
    
    async def test_user_referral_fields(self, db_session, mock_user_data):
        """Test user referral milestone fields"""
        user = User(**mock_user_data)
        user.referral_count = 5
        user.referral_milestone = 5
        user.referral_badge = "⭐ دوستیابی ستاره"
        
        db_session.add(user)
        await db_session.commit()
        
        assert user.referral_milestone == 5
        assert user.referral_badge is not None


@pytest.mark.unit
class TestCachedFileModel:
    """Test CachedFile model with unique constraints"""
    
    async def test_cached_file_creation(self, db_session):
        """Test creating a cached file"""
        cached_file = CachedFile(
            file_hash="hash123",
            url_hash="url_hash123",
            format_id="fmt_1",
            codec="h264",
            telegram_file_id="file_123",
            file_name="video.mp4",
            file_size=1024000,
            platform="youtube",
            video_id="vid123"
        )
        
        db_session.add(cached_file)
        await db_session.commit()
        
        assert cached_file.id is not None
        assert cached_file.url_hash == "url_hash123"
    
    async def test_cached_file_unique_constraint(self, db_session):
        """Test that unique constraint prevents duplicates"""
        file1 = CachedFile(
            file_hash="hash1",
            url_hash="url_hash",
            format_id="fmt",
            codec="h264",
            telegram_file_id="file1",
            file_name="video1.mp4",
            file_size=1000,
            platform="youtube"
        )
        
        file2 = CachedFile(
            file_hash="hash2",
            url_hash="url_hash",  # Same
            format_id="fmt",      # Same
            codec="h264",         # Same
            telegram_file_id="file2",
            file_name="video2.mp4",
            file_size=2000,
            platform="youtube"
        )
        
        db_session.add(file1)
        await db_session.commit()
        
        # Adding duplicate should fail
        db_session.add(file2)
        with pytest.raises(Exception):  # IntegrityError
            await db_session.commit()


@pytest.mark.unit
class TestPaymentModel:
    """Test Payment model"""
    
    async def test_payment_creation(self, db_session):
        """Test creating a payment"""
        payment = Payment(
            user_id=1,
            plan_id=1,
            amount=99.99,
            currency="USD",
            payment_method="cryptobot",
            status="pending"
        )
        
        db_session.add(payment)
        await db_session.commit()
        
        assert payment.id is not None
        assert payment.status == "pending"
        assert payment.payment_method == "cryptobot"


@pytest.mark.unit
class TestReferralModel:
    """Test Referral model"""
    
    async def test_referral_creation(self, db_session):
        """Test creating a referral"""
        referral = Referral(
            referrer_id=1,
            referred_user_id=2,
            status="pending"
        )
        
        db_session.add(referral)
        await db_session.commit()
        
        assert referral.id is not None
        assert referral.status == "pending"
        assert referral.reward_coins is None
