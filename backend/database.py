from __future__ import annotations 
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

DATABASE_URL = os.getenv("DATABASE_URL")

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
    # Use NullPool for async if needed
    poolclass=NullPool if os.getenv("ENV") == "test" else None,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# SQLModel metadata container kept for compatibility with the rest of the app and tests.
Base = SQLModel

# Dependency for getting database session
async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields a database session and ensures it's closed after the request is finished.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
