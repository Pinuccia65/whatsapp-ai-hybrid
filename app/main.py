"""
WhatsApp AI Receptionist - FastAPI Application

Entry point dell'applicazione. Configura FastAPI, middleware,
e registra tutti i router.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.utils.database import connect_to_mongo, close_mongo_connection
from app.utils.redis_client import connect_to_redis, close_redis_connection
from app.api.routes import webhook, bookings, tenants


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestisce startup e shutdown dell'applicazione."""
    # Startup
    print("🚀 Starting WhatsApp AI Receptionist...")
    await connect_to_mongo()
    await connect_to_redis()
    print("✅ Database connections established")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await close_mongo_connection()
    await close_redis_connection()
    print("✅ Connections closed")


# Crea applicazione FastAPI
app = FastAPI(
    title="WhatsApp AI Receptionist",
    description="Sistema di ricezione automatica per prenotazioni via WhatsApp con AI",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware (per admin dashboard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra router
app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["tenants"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "WhatsApp AI Receptionist",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Health check dettagliato."""
    return {
        "status": "healthy",
        "environment": settings.environment,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
    )