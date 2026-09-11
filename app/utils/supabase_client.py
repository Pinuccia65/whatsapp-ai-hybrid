"""
Supabase Client.

Sostituisce sia MongoDB che Redis.
Supabase offre PostgreSQL + API REST in un unico servizio.
"""

from supabase import create_client, Client
from app.config import settings

_supabase: Client = None


def init_supabase() -> Client:
    """Inizializza il client Supabase."""
    global _supabase
    _supabase = create_client(settings.supabase_url, settings.supabase_key)
    print("Connected to Supabase")
    return _supabase


def get_supabase() -> Client:
    """Ottiene il client Supabase."""
    if not _supabase:
        raise RuntimeError("Supabase not initialized")
    return _supabase