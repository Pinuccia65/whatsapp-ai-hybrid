"""
Redis client utilities.

Gestisce connessione Redis per storage sessioni conversazione.
"""

from redis.asyncio import Redis

from app.config import settings


_redis: Redis = None


async def connect_to_redis() -> None:
    """Connette a Redis."""
    global _redis
    
    _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    
    # Test connessione
    await _redis.ping()
    print("✅ Connected to Redis")


async def close_redis_connection() -> None:
    """Chiude connessione Redis."""
    global _redis
    
    if _redis:
        await _redis.close()
        print("✅ Redis connection closed")


async def get_redis() -> Redis:
    """Ottiene client Redis."""
    if not _redis:
        raise RuntimeError("Redis not initialized")
    return _redis