"""
FastAPI Dependencies.

Fornisce istanze di servizi e database connection
per injection nei route handlers.
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.utils.database import get_database
from app.utils.redis_client import get_redis


async def get_db() -> AsyncIOMotorDatabase:
    """Dependency: database MongoDB."""
    return await get_database()


async def get_redis_client() -> Redis:
    """Dependency: client Redis."""
    return await get_redis()