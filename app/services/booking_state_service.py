"""
Booking State Service - USA SUPABASE.

Le sessioni sono nella tabella 'sessions' di Supabase.
Sostituisce completamente Redis.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from app.config import settings
from app.schemas.booking import BookingState
from app.utils.supabase_client import get_supabase


class NextAction:
    def __init__(self, type: str, message: str, field: str = None, options: List[Dict] = None):
        self.type = type
        self.message = message
        self.field = field
        self.options = options or []


class BookingStateService:
    """Gestisce stato conversazioni in Supabase."""
    
    async def get_state(self, phone_number: str, tenant_id: str) -> Optional[BookingState]:
        """Recupera stato da Supabase (sostituisce Redis GET)."""
        supabase = get_supabase()
        response = supabase.table("sessions").select("*").eq(
            "tenant_id", tenant_id
        ).eq("phone_number", phone_number).gt(
            "expires_at", datetime.utcnow().isoformat()
        ).execute()
        
        if not response.data:
            return None
        return self._row_to_state(response.data[0])
    
    async def save_state(self, state: BookingState) -> None:
        """Salva stato in Supabase (sostituisce Redis SET)."""
        supabase = get_supabase()
        expires_at = (datetime.utcnow() + timedelta(hours=settings.session_ttl_hours)).isoformat()
        
        supabase.table("sessions").upsert({
            "tenant_id": state.tenant_id,
            "phone_number": state.phone_number,
            "conversation_id": state.conversation_id,
            "intent": state.intent,
            "party_size": state.party_size,
            "time_preference": state.time_preference,
            "booking_date": state.date,
            "booking_time": state.time,
            "service_id": state.service_id,
            "customer_name": state.customer_name,
            "status": state.status,
            "expires_at": expires_at,
        }, on_conflict="tenant_id,phone_number").execute()
    
    def create_initial_state(self, phone_number: str, tenant_id: str, extraction: dict) -> BookingState:
        return BookingState(
            conversation_id=str(uuid.uuid4()),
            phone_number=phone_number,
            tenant_id=tenant_id,
            intent=extraction.get("intent") or "create",
            party_size=extraction.get("party_size"),
            time_preference=extraction.get("time_preference"),
            date=extraction.get("date"),
            time=extraction.get("time"),
            status="collecting",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    
    def handle_button_response(self, state: BookingState, payload: str) -> BookingState:
        parts = payload.split(":", 1)
        if len(parts) != 2:
            return state
        
        field, value = parts
        updates = {}
        if field == "party_size": updates["party_size"] = int(value)
        elif field == "time_preference": updates["time_preference"] = value
        elif field == "date": updates["date"] = value
        elif field == "time": updates["time"] = value
        elif field == "confirm": updates["status"] = "completed" if value == "yes" else "cancelled"
        
        d = state.dict()
        d.update(updates)
        d["updated_at"] = datetime.utcnow()
        return BookingState(**d)
    
    def update_state(self, state: BookingState, update: dict) -> BookingState:
        d = state.dict()
        d.update(update)
        d["updated_at"] = datetime.utcnow()
        return BookingState(**d)
    
    def get_next_action(self, state: BookingState, tenant: dict, availability: dict) -> NextAction:
        if self._is_complete(state):
            return NextAction("confirm", self._confirm_msg(state), options=[
                {"id": "confirm:yes", "label": "Conferma"},
                {"id": "confirm:no", "label": "Modifica"},
            ])
        
        missing = self._next_missing(state)
        
        if missing == "party_size":
            return NextAction("ask", "Per quante persone?", "party_size", [
                {"id": f"party_size:{i}", "label": f"{i} {'persona' if i==1 else 'persone'}"} for i in range(1, 9)
            ])
        elif missing == "time_preference":
            prefs = [p for p in tenant.get("time_preferences", []) if p["pref_key"] in availability.get("preferences_with_availability", [])]
            return NextAction("ask", "Quale fascia oraria?", "time_preference", [
                {"id": f"time_preference:{p['pref_key']}", "label": p["label"]} for p in prefs
            ])
        elif missing == "date":
            days = availability.get("days", [])[:10]
            return NextAction("ask", "Quale giorno?", "date", [
                {"id": f"date:{d['date']}", "label": d["day_label"]} for d in days
            ])
        elif missing == "time":
            day = next((d for d in availability.get("days", []) if d["date"] == state.date), None)
            if not day:
                return NextAction("ask", "Nessuna disponibilita per questo giorno.")
            return NextAction("ask", "Scegli orario:", "time", [
                {"id": f"time:{s['time']}", "label": s["time"]} for s in day["slots"]
            ])
        
        return NextAction("ask", "Come posso aiutarti?")
    
    def _is_complete(self, state: BookingState) -> bool:
        return all([state.intent, state.party_size, state.time_preference, state.date, state.time])
    
    def _next_missing(self, state: BookingState) -> Optional[str]:
        if not state.party_size: return "party_size"
        if not state.time_preference: return "time_preference"
        if not state.date: return "date"
        if not state.time: return "time"
        return None
    
    def _confirm_msg(self, state: BookingState) -> str:
        return f"Riepilogo:\n\nData: {state.date}\nOra: {state.time}\nPersone: {state.party_size}\n\nConfermi?"
    
    def _row_to_state(self, row: dict) -> BookingState:
        return BookingState(
            conversation_id=row["conversation_id"],
            phone_number=row["phone_number"],
            tenant_id=row["tenant_id"],
            intent=row.get("intent"),
            party_size=row.get("party_size"),
            time_preference=row.get("time_preference"),
            date=row.get("booking_date"),
            time=row.get("booking_time"),
            service_id=row.get("service_id"),
            customer_name=row.get("customer_name"),
            status=row.get("status", "collecting"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )