"""Booking Service - Supabase."""

from typing import Optional, List
from datetime import date, datetime

from app.utils.supabase_client import get_supabase
from app.schemas.booking import BookingCreate, BookingState


class BookingService:
    async def list_bookings(self, tenant_id: str, date_from: date = None, date_to: date = None, status: str = None) -> List[dict]:
        supabase = get_supabase()
        q = supabase.table("bookings").select("*").eq("tenant_id", tenant_id)
        if date_from: q = q.gte("booking_date", date_from.isoformat())
        if date_to: q = q.lte("booking_date", date_to.isoformat())
        if status: q = q.eq("status", status)
        return (q.order("booking_date").order("booking_time").execute().data or [])
    
    async def get_booking(self, booking_id: str) -> Optional[dict]:
        supabase = get_supabase()
        r = supabase.table("bookings").select("*").eq("id", booking_id).execute()
        return r.data[0] if r.data else None
    
    async def create_booking(self, data: BookingCreate) -> dict:
        supabase = get_supabase()
        r = supabase.table("bookings").insert({
            "tenant_id": data.tenant_id, "phone_number": data.phone_number,
            "customer_name": data.customer_name, "intent": "create",
            "party_size": data.party_size, "booking_date": data.date,
            "booking_time": data.time, "status": "confirmed",
            "confirmed_at": datetime.utcnow().isoformat(),
        }).execute()
        return r.data[0]
    
    async def create_from_state(self, state: BookingState) -> dict:
        supabase = get_supabase()
        r = supabase.table("bookings").insert({
            "tenant_id": state.tenant_id, "phone_number": state.phone_number,
            "customer_name": state.customer_name, "intent": state.intent or "create",
            "party_size": state.party_size or 1, "booking_date": state.date,
            "booking_time": state.time, "time_preference": state.time_preference,
            "status": "confirmed", "confirmed_at": datetime.utcnow().isoformat(),
        }).execute()
        return r.data[0]
    
    async def update_status(self, booking_id: str, status: str) -> Optional[dict]:
        supabase = get_supabase()
        r = supabase.table("bookings").update({"status": status}).eq("id", booking_id).execute()
        return r.data[0] if r.data else None
    
    async def cancel_booking(self, booking_id: str) -> None:
        supabase = get_supabase()
        supabase.table("bookings").update({"status": "cancelled"}).eq("id", booking_id).execute()