"""
Database utilities.

Gestisce connessione MongoDB con Beanie ODM.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings
from app.models.tenant import TenantModel
from app.models.booking import BookingModel


_client: AsyncIOMotorClient = None


async def connect_to_mongo() -> None:
    """Connette a MongoDB e inizializza Beanie."""
    global _client
    
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    
    # Inizializza Beanie con i modelli
    await init_beanie(
        database=_client[settings.mongodb_db_name],
        document_models=[TenantModel, BookingModel],
    )
    
    print("✅ Connected to MongoDB")


async def close_mongo_connection() -> None:
    """Chiude connessione MongoDB."""
    global _client
    
    if _client:
        _client.close()
        print("✅ MongoDB connection closed")


async def get_database():
    """Ottiene istanza database."""
    if not _client:
        raise RuntimeError("Database not initialized")
    return _client[settings.mongodb_db_name]