"""Configurazione applicazione con pydantic-settings."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    
    # Application
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Supabase (sostituisce MongoDB + Redis)
    supabase_url: str = ""
    supabase_key: str = ""
    session_ttl_hours: int = 24
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.0
    
    # WhatsApp
    whatsapp_token: str = ""
    whatsapp_verify_token: str = ""
    whatsapp_api_url: str = "https://graph.facebook.com/v18.0"


settings = Settings()