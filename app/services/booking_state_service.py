"""
Booking State Service.

Gestisce lo stato della conversazione per ogni utente.
Utilizza Redis per persistenza con TTL.
"""

import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from redis.asyncio import Redis

from app.config import settings
from app.schemas.booking import BookingState, BookingIntent
from app.schemas.tenant import Tenant
from app.services.availability_engine import AvailabilityResult
from app.utils.redis_client import get_redis


class NextAction:
    """Rappresenta la prossima azione da intraprendere."""
    
    def __init__(
        self,
        type: str,  # 'ask', 'confirm', 'complete'
        message: str,
        field: Optional[str] = None,
        options: Optional[List[Dict[str, str]]] = None,
    ):
        self.type = type
        self.message = message
        self.field = field
        self.options = options or []


class BookingStateService:
    """Gestisce lo stato delle conversazioni."""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
    
    async def _get_redis(self) -> Redis:
        """Ottiene client Redis."""
        if not self.redis:
            self.redis = await get_redis()
        return self.redis
    
    def _make_key(self, tenant_id: str, phone_number: str) -> str:
        """Crea la chiave Redis per lo stato."""
        return f"state:{tenant_id}:{phone_number}"
    
    async def get_state(self, phone_number: str, tenant_id: str) -> Optional[BookingState]:
        """Recupera lo stato della conversazione."""
        redis = await self._get_redis()
        key = self._make_key(tenant_id, phone_number)
        
        data = await redis.get(key)
        if not data:
            return None
        
        state_dict = json.loads(data)
        return BookingState(**state_dict)
    
    async def save_state(self, state: BookingState) -> None:
        """Salva lo stato della conversazione."""
        redis = await self._get_redis()
        key = self._make_key(state.tenant_id, state.phone_number)
        
        state.updated_at = datetime.utcnow()
        data = json.dumps(state.dict(), default=str)
        
        # TTL 24 ore
        await redis.setex(key, settings.redis_session_ttl, data)
    
    def create_initial_state(
        self,
        phone_number: str,
        tenant_id: str,
        extraction: Dict[str, Any],
    ) -> BookingState:
        """Crea stato iniziale da estrazione AI."""
        return BookingState(
            conversation_id=str(uuid.uuid4()),
            phone_number=phone_number,
            tenant_id=tenant_id,
            intent=extraction.get("intent") or "create",
            party_size=extraction.get("party_size"),
            time_preference=extraction.get("time_preference"),
            date=extraction.get("date"),
            time=extraction.get("time"),
            service_id=extraction.get("service_id"),
            customer_name=extraction.get("customer_name"),
            status="collecting",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    
    def handle_button_response(self, state: BookingState, payload: str) -> BookingState:
        """
        Gestisce risposta da bottone WhatsApp.
        
        Formato payload: "field:value" (es: "time:19:30")
        """
        parts = payload.split(":", 1)
        if len(parts) != 2:
            return state
        
        field, value = parts
        
        # Aggiorna il campo appropriato
        updates = {}
        if field == "party_size":
            updates["party_size"] = int(value)
        elif field == "time_preference":
            updates["time_preference"] = value
        elif field == "date":
            updates["date"] = value
        elif field == "time":
            updates["time"] = value
        elif field == "confirm":
            if value == "yes":
                updates["status"] = "completed"
            else:
                updates["status"] = "cancelled"
        
        # Crea nuovo stato con aggiornamenti
        state_dict = state.dict()
        state_dict.update(updates)
        state_dict["updated_at"] = datetime.utcnow()
        
        return BookingState(**state_dict)
    
    def update_state(self, state: BookingState, update: Dict[str, Any]) -> BookingState:
        """Aggiorna lo stato con nuovi dati."""
        state_dict = state.dict()
        state_dict.update(update)
        state_dict["updated_at"] = datetime.utcnow()
        
        return BookingState(**state_dict)
    
    def get_next_action(
        self,
        state: BookingState,
        tenant: Tenant,
        availability: AvailabilityResult,
    ) -> NextAction:
        """
        Determina la prossima azione da intraprendere.
        
        Logica:
        1. Se tutti i parametri sono completi → conferma
        2. Altrimenti → chiedi il prossimo campo mancante
        """
        # Se stato completo → conferma
        if self._is_state_complete(state):
            return NextAction(
                type="confirm",
                message=self._build_confirmation_message(state),
                options=[
                    {"id": "confirm:yes", "label": "✅ Conferma"},
                    {"id": "confirm:no", "label": "✏️ Modifica"},
                ],
            )
        
        # Determina prossimo campo mancante
        missing_field = self._get_next_missing_field(state)
        
        if missing_field == "party_size":
            return NextAction(
                type="ask",
                field="party_size",
                message="Per quante persone?",
                options=[
                    {"id": f"party_size:{i}", "label": f"{i} {'persona' if i == 1 else 'persone'}"}
                    for i in range(1, 9)
                ],
            )
        
        elif missing_field == "time_preference":
            # Mostra solo fasce con disponibilità
            available_prefs = [
                p for p in tenant.time_preferences
                if p.id in availability.preferences_with_availability
            ]
            return NextAction(
                type="ask",
                field="time_preference",
                message="Quale fascia oraria preferisci?",
                options=[
                    {"id": f"time_preference:{p.id}", "label": p.label}
                    for p in available_prefs
                ],
            )
        
        elif missing_field == "date":
            # Mostra giorni disponibili (max 10)
            days = availability.days[:10]
            return NextAction(
                type="ask",
                field="date",
                message="Quale giorno preferisci?",
                options=[
                    {"id": f"date:{d.date}", "label": d.day_label}
                    for d in days
                ],
            )
        
        elif missing_field == "time":
            # Mostra slot per il giorno scelto
            day_slots = next((d for d in availability.days if d.date == state.date), None)
            if not day_slots:
                return NextAction(
                    type="ask",
                    message="Mi dispiace, non ci sono disponibilità per questo giorno.",
                    options=[],
                )
            
            return NextAction(
                type="ask",
                field="time",
                message="Scegli un orario:",
                options=[
                    {"id": f"time:{s.time}", "label": s.time}
                    for s in day_slots.slots
                ],
            )
        
        # Fallback
        return NextAction(
            type="ask",
            message="Come posso aiutarti?",
            options=[],
        )
    
    def _is_state_complete(self, state: BookingState) -> bool:
        """Verifica se tutti i parametri necessari sono presenti."""
        return all([
            state.intent,
            state.party_size,
            state.time_preference,
            state.date,
            state.time,
        ])
    
    def _get_next_missing_field(self, state: BookingState) -> Optional[str]:
        """Determina il prossimo campo da chiedere."""
        if not state.party_size:
            return "party_size"
        if not state.time_preference:
            return "time_preference"
        if not state.date:
            return "date"
        if not state.time:
            return "time"
        return None
    
    def _build_confirmation_message(self, state: BookingState) -> str:
        """Costruisce messaggio di conferma."""
        return (
            f"Perfetto! Riepilogo:\n\n"
            f"📅 {state.date}\n"
            f"⏰ Ore {state.time}\n"
            f"👥 {state.party_size} {'persona' if state.party_size == 1 else 'persone'}\n\n"
            f"Confermi?"
        )