"""
Tenant Schemas.

Definisce gli schemi Pydantic per validazione e serializzazione
della configurazione tenant.
"""

from typing import List, Optional
from datetime import datetime
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
    """Orari di apertura."""
    day_of_week: int  # 0 = domenica
    open: str  # HH:mm
    close: str  # HH:mm


class Exception(BaseModel):
    """Eccezione."""
    date: str
    type: str
    open: Optional[str] = None
    close: Optional[str] = None
    reason: Optional[str] = None


class BookingRules(BaseModel):
    """Regole prenotazione."""
    min_advance_hours: int = 2
    max_advance_days: int = 30
    slot_interval_minutes: int = 30
    max_party_size: int = 20
    min_party_size: int = 1


class Tenant(BaseModel):
    """Schema risposta tenant."""
    id: str
    name: str
    type: str
    
    time_preferences: List[TimePreference]
    services: List[Service]
    opening_hours: List[OpeningHours]
    exceptions: List[Exception] = []
    booking_rules: BookingRules
    
    whatsapp_phone_number_id: str
    welcome_message: Optional[str] = None
    
    capacity: int
    
    created_at: datetime
    updated_at: datetime


class TenantCreate(BaseModel):
    """Schema creazione tenant."""
    name: str
    type: str
    time_preferences: List[TimePreference]
    services: List[Service]
    opening_hours: List[OpeningHours]
    booking_rules: BookingRules
    whatsapp_phone_number_id: str
    capacity: int
    welcome_message: Optional[str] = None


class TenantUpdate(BaseModel):
    """Schema aggiornamento tenant (tutti i campi opzionali)."""
    name: Optional[str] = None
    type: Optional[str] = None
    time_preferences: Optional[List[TimePreference]] = None
    services: Optional[List[Service]] = None
    opening_hours: Optional[List[OpeningHours]] = None
    exceptions: Optional[List[Exception]] = None
    booking_rules: Optional[BookingRules] = None
    welcome_message: Optional[str] = None
    capacity: Optional[int] = None