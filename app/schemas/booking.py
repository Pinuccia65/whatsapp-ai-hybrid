"""Booking Schemas."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Booking(BaseModel):
    id: str = ""
    tenant_id: str = ""
    phone_number: str = ""
    customer_name: Optional[str] = None
    intent: str = "create"
    party_size: int = 1
    booking_date: str = ""
    booking_time: str = ""
    time_preference: Optional[str] = None
    service_id: Optional[str] = None
    status: str = "pending"
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    confirmed_at: Optional[str] = None


class BookingCreate(BaseModel):
    tenant_id: str
    phone_number: str
    party_size: int = Field(ge=1, le=100)
    date: str
    time: str
    service_id: Optional[str] = None
    customer_name: Optional[str] = None


class BookingState(BaseModel):
    conversation_id: str
    phone_number: str
    tenant_id: str
    intent: Optional[str] = None
    party_size: Optional[int] = None
    time_preference: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    service_id: Optional[str] = None
    customer_name: Optional[str] = None
    status: str = "collecting"
    last_question: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None