"""WhatsApp AI Receptionist - FastAPI Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.utils.supabase_client import init_supabase
from app.api.routes import webhook, bookings, tenants


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown."""
    print("Starting WhatsApp AI Receptionist...")
    init_supabase()
    print("Supabase connection established")
    yield
    print("Shutting down...")


app = FastAPI(
    title="WhatsApp AI Receptionist",
    description="Sistema prenotazioni WhatsApp con AI - Supabase + FastAPI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["tenants"])


@app.get("/")
async def root():
    return {"status": "ok", "service": "WhatsApp AI Receptionist", "db": "Supabase"}


@app.get("/health")
async def health():
    return {"status": "healthy", "environment": settings.environment}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)