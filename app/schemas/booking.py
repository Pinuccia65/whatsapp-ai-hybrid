"""
Booking Schemas.

Definisce gli schemi Pydantic per validazione e serializzazione
delle prenotazioni.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class BookingStatus(str, Enum):
    """Stato della prenotazione."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class BookingIntent(str, Enum):
    """Intent della prenotazione."""
    CREATE = "create"
    MOVE = "move"
    CANCEL = "cancel"


class Booking(BaseModel):
    """Schema risposta prenotazione."""
    id: str
    tenant_id: str
    phone_number: str
    customer_name: Optional[str] = None
    
    intent: str
    party_size: int
    date: str
    time: str
    time_preference: Optional[str] = None
    service_id: Optional[str] = None
    
    status: str
    notes: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = None


class BookingCreate(BaseModel):
    """Schema creazione prenotazione."""
    tenant_id: str
    phone_number: str
    party_size: int = Field(ge=1, le=100)
    date: str  # YYYY-MM-DD
    time: str  # HH:mm
    service_id: Optional[str] = None
    customer_name: Optional[str] = None
    notes: Optional[str] = None


class BookingState(BaseModel):
    """Stato della conversazione di prenotazione."""
    conversation_id: str
    phone_number: str
    tenant_id: str
    
    # Parametri raccolta
    intent: Optional[str] = None
    party_size: Optional[int] = None
    time_preference: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    service_id: Optional[str] = None
    customer_name: Optional[str] = None
    
    # Stato conversazione
    status: str = "collecting"  # 'collecting' | 'confirming' | 'completed' | 'cancelled'
    last_question: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime