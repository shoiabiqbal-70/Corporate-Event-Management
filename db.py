
"""
Database configuration for Corporate Event Management API.

Uses SQLAlchemy 2.0 asynchronous database operations
with Neon PostgreSQL.
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.engine import make_url

from env import settings


# =========================================================
# 1. DATABASE CONNECTION
# =========================================================

database_url = make_url(settings.DATABASE_URL)

# Convert PostgreSQL URL to asyncpg format.
if database_url.drivername in ("postgres", "postgresql"):
    database_url = database_url.set(
        drivername="postgresql+asyncpg"
    )

# Remove parameters handled separately by asyncpg.
query_parameters = dict(database_url.query)
query_parameters.pop("sslmode", None)
query_parameters.pop("channel_binding", None)

database_url = database_url.set(query=query_parameters)


# Create asynchronous database engine.
engine = create_async_engine(
    database_url,
    echo=False,
    pool_pre_ping=True,
    connect_args={"ssl": "require"},
)


# =========================================================
# 2. DATABASE SESSION
# =========================================================

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# =========================================================
# 3. BASE MODEL
# =========================================================

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


# =========================================================
# 4. DATABASE DEPENDENCY
# =========================================================

async def get_db():
    """Provide an asynchronous database session."""

    async with AsyncSessionLocal() as session:
        yield session


# =========================================================
# 5. CREATE DATABASE TABLES
# =========================================================

async def create_tables():
    """Create all database tables in Neon PostgreSQL."""

    # Import models so SQLAlchemy registers all tables.
    from models import User, Event, Registration

    async with engine.begin() as connection:

        await connection.run_sync(
            Base.metadata.create_all
        )

    print("Database tables created successfully!")


# =========================================================
# 6. CHECK DATABASE CONNECTION
# =========================================================

async def check_database_connection():
    """Check whether Neon PostgreSQL is accessible."""

    from sqlalchemy import text

    async with engine.connect() as connection:

        result = await connection.execute(
            text("SELECT 1")
        )

        return result.scalar_one()


# =========================================================
# 7. CLOSE DATABASE CONNECTION
# =========================================================

async def close_database_connection():
    """Close the database engine."""

    await engine.dispose()
