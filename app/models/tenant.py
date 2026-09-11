"""
Tenant Model.

Definisce lo schema MongoDB per i tenant utilizzando Beanie ODM.
"""

from typing import List, Optional
from datetime import datetime
from beanie import Document, Indexed
from pydantic import BaseModel, Field


class TimePreference(BaseModel):
    """Fascia oraria."""
    id: str
    label: str
    from_time: str = Field(alias="from")  # HH:mm
    to_time: str = Field(alias="to")  # HH:mm
    
    class Config:
        populate_by_name = True


class Service(BaseModel):
    """Servizio offerto."""
    id: str
    name: str
    duration_minutes: int
    description: Optional[str] = None


class OpeningHours(BaseModel):
    """Orari di apertura per giorno."""
    day_of_week: int  # 0 = domenica, 6 = sabato
    open: str  # HH:mm
    close: str  # HH:mm


class Exception(BaseModel):
    """Eccezione (chiusura, orari speciali)."""
    date: str  # YYYY-MM-DD
    type: str  # 'closed' | 'special_hours'
    open: Optional[str] = None
    close: Optional[str] = None
    reason: Optional[str] = None


class BookingRules(BaseModel):
    """Regole di prenotazione."""
    min_advance_hours: int = 2
    max_advance_days: int = 30
    slot_interval_minutes: int = 30
    max_party_size: int = 20
    min_party_size: int = 1


class TenantModel(Document):
    """Modello MongoDB per Tenant."""
    
    name: str
    type: str  # 'restaurant' | 'medical' | 'barber' | 'beauty' | 'generic'
    
    # Configurazione
    time_preferences: List[TimePreference]
    services: List[Service]
    opening_hours: List[OpeningHours]
    exceptions: List[Exception] = []
    booking_rules: BookingRules
    
    # WhatsApp
    whatsapp_phone_number_id: Indexed(str, unique=True)
    welcome_message: Optional[str] = None
    
    # Capacità
    capacity: int
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "tenants"
    
    def to_dict(self) -> dict:
        """Converte in dizionario."""
        data = self.dict()
        data["id"] = str(self.id)
        return data


# Tipo esportato per uso nei servizi
Tenant = dict