
"""
Shared pytest fixtures for the Corporate Event Management API.

Uses an isolated in-memory SQLite database instead of Neon.
"""

import pytest_asyncio

from httpx import ASGITransport, AsyncClient

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from sqlalchemy.pool import StaticPool

from db import Base, get_db
from models import User, Event, Registration
from main import app


# =========================================================
# 1. CREATE TEMPORARY TEST DATABASE
# =========================================================

@pytest_asyncio.fixture
async def test_engine():
    """Create an isolated in-memory SQLite database."""

    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    # Remove all test tables after testing.
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# =========================================================
# 2. CREATE TEST DATABASE SESSION
# =========================================================

@pytest_asyncio.fixture
async def test_db(test_engine):
    """Provide a session connected to the test database."""

    TestingSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with TestingSessionLocal() as session:
        yield session


# =========================================================
# 3. OVERRIDE DATABASE DEPENDENCY
# =========================================================

@pytest_asyncio.fixture
async def override_database(test_engine):
    """Make API requests use SQLite instead of Neon."""

    TestingSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()


# =========================================================
# 4. CREATE TEST HTTP CLIENT
# =========================================================

@pytest_asyncio.fixture
async def client(test_engine, override_database):
    """Create an asynchronous HTTP client for API testing."""

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as test_client:

        yield test_client
