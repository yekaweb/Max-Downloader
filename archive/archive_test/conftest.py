"""Pytest configuration and shared fixtures"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.models import Base


@pytest.fixture(scope="session")
def event_loop():
    """Create and provide event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """Create in-memory SQLite database for testing"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine):
    """Create database session for testing"""
    async_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        future=True
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def mock_user_data():
    """Sample user data for testing"""
    return {
        "telegram_id": 123456789,
        "telegram_username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "language": "en",
        "preferred_quality": "best"
    }


@pytest.fixture
def mock_download_url():
    """Sample download URLs"""
    return {
        "youtube": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "instagram": "https://www.instagram.com/p/ABC123/",
        "twitter": "https://twitter.com/user/status/123456789",
        "tiktok": "https://www.tiktok.com/@user/video/123456789",
        "direct": "https://example.com/video.mp4"
    }


@pytest.fixture
def mock_progress_data():
    """Sample progress data"""
    return {
        "title": "Test Video",
        "progress_percent": 50.0,
        "downloaded_mb": 125.5,
        "total_mb": 251.0,
        "speed_mbps": 5.2,
        "eta_seconds": 24,
        "queue_position": 0,
        "phase": "download"
    }
