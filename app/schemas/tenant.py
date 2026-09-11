"""Tenant Schemas."""

from typing import List, Optional
from pydantic import BaseModel


class Tenant(BaseModel):
    id: str = ""
    name: str = ""
    type: str = ""
    time_preferences: List[dict] = []
    services: List[dict] = []
    opening_hours: List[dict] = []
    exceptions: List[dict] = []
    whatsapp_phone_number_id: str = ""
    capacity: int = 20


class TenantCreate(BaseModel):
    name: str
    type: str
    time_preferences: List[dict]
    services: List[dict]
    opening_hours: List[dict]
    whatsapp_phone_number_id: str
    capacity: int = 20


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None