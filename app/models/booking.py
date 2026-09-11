"""
Booking Model.

Definisce lo schema MongoDB per le prenotazioni utilizzando Beanie ODM.
"""

from typing import Optional
from datetime import datetime
from beanie import Document, Indexed
from pydantic import Field


class BookingModel(Document):
    """Modello MongoDB per Booking."""
    
    tenant_id: Indexed(str)
    phone_number: Indexed(str)
    customer_name: Optional[str] = None
    
    # Parametri prenotazione
    intent: str  # 'create' | 'move' | 'cancel'
    party_size: int
    date: str  # YYYY-MM-DD
    time: str  # HH:mm
    time_preference: Optional[str] = None
    service_id: Optional[str] = None
    
    # Stato
    status: Indexed(str) = "pending"  # 'pending' | 'confirmed' | 'cancelled' | 'completed'
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    
    class Settings:
        name = "bookings"
        indexes = [
            # Compound index per query efficienti
            [("tenant_id", 1), ("date", 1), ("time", 1)],
            [("tenant_id", 1), ("phone_number", 1)],
        ]
    
    def to_dict(self) -> dict:
        """Converte in dizionario."""
        data = self.dict()
        data["id"] = str(self.id)
        return data


# Tipo esportato per uso nei servizi
Booking = dict