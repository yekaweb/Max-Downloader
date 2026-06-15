"""
Shared pytest fixtures for Max-Downloader test suite.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(scope="session")
def event_loop():
    """Use one event loop per test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db():
    """Return an AsyncSession mock with common methods pre-configured."""
    db = AsyncMock(spec=AsyncSession)
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.fixture
def mock_bot():
    """Minimal aiogram Bot mock."""
    bot = AsyncMock()
    bot.send_message = AsyncMock(return_value=MagicMock(message_id=1))
    bot.send_video = AsyncMock()
    bot.send_audio = AsyncMock()
    bot.send_document = AsyncMock()
    bot.get_me = AsyncMock(return_value=MagicMock(username="test_bot"))
    return bot
