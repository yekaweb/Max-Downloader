"""Database connection using SQLAlchemy Async engine"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config_simple import settings

# Use async URL for runtime
engine = create_async_engine(settings.database_async_url, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

__all__ = ["engine", "AsyncSessionLocal", "get_db"]
