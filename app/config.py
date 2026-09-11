"""
Configurazione applicazione.

Carica le variabili da .env e le valida con pydantic.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurazione globale dell'applicazione."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017/receptionist"
    mongodb_db_name: str = "receptionist"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_session_ttl: int = 86400  # 24 ore in secondi
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.0
    
    # WhatsApp Business API
    whatsapp_token: str = ""
    whatsapp_verify_token: str = ""
    whatsapp_api_url: str = "https://graph.facebook.com/v18.0"
    
    # Booking defaults
    default_slot_interval_minutes: int = 30
    default_max_advance_days: int = 30
    default_min_advance_hours: int = 2


# Istanza globale delle settings
settings = Settings()  # type: ignore