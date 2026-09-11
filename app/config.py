"""
Configurazione applicazione.

IMPORTANTE: Su Render le variabili d'ambiente si impostano nel dashboard,
NON tramite file .env. Pydantic-settings legge automaticamente da os.environ.
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    cors_origins: List[str] = ["*"]
    
    # Supabase - LETTO DA ENVIRONMENT VARIABLES
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    session_ttl_hours: int = 24
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.0
    
    # WhatsApp
    whatsapp_token: str = os.getenv("WHATSAPP_TOKEN", "")
    whatsapp_verify_token: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
    whatsapp_phone_number_id: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    whatsapp_api_url: str = os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v18.0")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()


def validate_settings():
    """Valida che le variabili critiche siano impostate."""
    errors = []
    
    if not settings.supabase_url:
        errors.append("SUPABASE_URL non impostata")
    if not settings.supabase_key:
        errors.append("SUPABASE_KEY non impostata")
    if not settings.openai_api_key:
        errors.append("OPENAI_API_KEY non impostata")
    if not settings.whatsapp_token:
        errors.append("WHATSAPP_TOKEN non impostata")
    if not settings.whatsapp_phone_number_id:
        errors.append("WHATSAPP_PHONE_NUMBER_ID non impostata")
    
    if errors:
        print("WARNING: Configurazione incompleta:")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print("Configuration OK")
    print(f"  Supabase URL: {settings.supabase_url[:30]}...")
    print(f"  Supabase Key: {settings.supabase_key[:20]}...")
    print(f"  OpenAI: {'configured' if settings.openai_api_key else 'MISSING'}")
    print(f"  WhatsApp Token: {'configured' if settings.whatsapp_token else 'MISSING'}")
    print(f"  WhatsApp Phone Number ID: {settings.whatsapp_phone_number_id}")
    return True
