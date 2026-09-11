"""
Availability Engine.

Calcola la disponibilità REALE combinando:
- Configurazione tenant (fasce orarie, servizi)
- Giorni di apertura
- Eccezioni (festività, chiusure)
- Prenotazioni esistenti
- Regole di capacità
"""

from datetime import datetime, timedelta, date
from typing import Optional, List
from pydantic import BaseModel

from app.models.tenant import TenantModel
from app.models.booking import BookingModel
from app.utils.date_utils import time_to_minutes, is_time_in_preference


class TimeSlot(BaseModel):
    """Slot temporale disponibile."""
    time: str  # HH:mm
    available: bool = True


class DayAvailability(BaseModel):
    """Disponibilità per un singolo giorno."""
    date: str  # YYYY-MM-DD
    day_of_week: int  # 0 = domenica
    day_label: str  # "Sab 12"
    slots: List[TimeSlot]
    slot_count: int


class AvailabilityResult(BaseModel):
    """Risultato completo del calcolo disponibilità."""
    days: List[DayAvailability]
    total_slots: int
    has_availability: bool
    preferences_with_availability: List[str]


class AvailabilityParams(BaseModel):
    """Parametri per il calcolo disponibilità."""
    tenant_id: str
    time_preference: Optional[str] = None
    date: Optional[str] = None
    party_size: Optional[int] = None


DAYS_SHORT = ["Dom", "Lun", "Mar", "Mer", "Gio", "Ven", "Sab"]


class AvailabilityEngine:
    """Engine per calcolo disponibilità."""
    
    async def calculate(
        self,
        tenant_id: str,
        time_preference: Optional[str] = None,
        date: Optional[str] = None,
        party_size: Optional[int] = None,
    ) -> AvailabilityResult:
        """
        Calcola disponibilità per i prossimi N giorni.
        
        Args:
            tenant_id: ID del tenant
            time_preference: Fascia oraria preferita (opzionale)
            date: Data specifica (opzionale)
            party_size: Numero persone (opzionale)
            
        Returns:
            AvailabilityResult con giorni e slot disponibili
        """
        # 1. Carica tenant
        tenant_doc = await TenantModel.find_one(TenantModel.id == tenant_id)
        if not tenant_doc:
            raise ValueError(f"Tenant not found: {tenant_id}")
        
        tenant = tenant_doc.to_dict()
        
        # 2. Genera periodo di ricerca
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=tenant["booking_rules"]["max_advance_days"])
        
        # 3. Recupera prenotazioni esistenti
        existing_bookings = await BookingModel.find(
            BookingModel.tenant_id == tenant_id,
            BookingModel.status == "confirmed",
            BookingModel.date >= start_date.isoformat(),
            BookingModel.date <= end_date.isoformat(),
        ).to_list()
        
        # 4. Calcola disponibilità per ogni giorno
        days: List[DayAvailability] = []
        preferences_with_availability = set()
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            day_of_week = current_date.weekday()
            # Converti da Monday=0 a Sunday=0
            day_of_week = (day_of_week + 1) % 7
            
            # Trova orari di apertura per questo giorno
            opening_hours = next(
                (oh for oh in tenant["opening_hours"] if oh["day_of_week"] == day_of_week),
                None
            )
            
            if opening_hours and not self._is_exception_closed(tenant, date_str):
                # Filtra prenotazioni per questo giorno
                day_bookings = [b for b in existing_bookings if b.date == date_str]
                
                # Calcola slot disponibili
                slots = self._calculate_day_slots(
                    opening_hours=opening_hours,
                    tenant=tenant,
                    day_bookings=day_bookings,
                    time_preference=time_preference,
                    party_size=party_size,
                )
                
                if slots:
                    # Determina quali fasce hanno disponibilità
                    for slot in slots:
                        for pref in tenant["time_preferences"]:
                            if is_time_in_preference(slot.time, pref["from_time"], pref["to_time"]):
                                preferences_with_availability.add(pref["id"])
                    
                    day_label = f"{DAYS_SHORT[day_of_week]} {current_date.day}"
                    days.append(DayAvailability(
                        date=date_str,
                        day_of_week=day_of_week,
                        day_label=day_label,
                        slots=slots,
                        slot_count=len(slots),
                    ))
            
            current_date += timedelta(days=1)
        
        return AvailabilityResult(
            days=days,
            total_slots=sum(d.slot_count for d in days),
            has_availability=len(days) > 0,
            preferences_with_availability=list(preferences_with_availability),
        )
    
    def _calculate_day_slots(
        self,
        opening_hours: dict,
        tenant: dict,
        day_bookings: list,
        time_preference: Optional[str],
        party_size: Optional[int],
    ) -> List[TimeSlot]:
        """Calcola slot disponibili per un singolo giorno."""
        slots: List[TimeSlot] = []
        interval = tenant["booking_rules"]["slot_interval_minutes"]
        service_duration = tenant["services"][0]["duration_minutes"] if tenant["services"] else 60
        
        # Parsing orari apertura
        open_h, open_m = map(int, opening_hours["open"].split(":"))
        close_h, close_m = map(int, opening_hours["close"].split(":"))
        
        current_minutes = open_h * 60 + open_m
        end_minutes = close_h * 60 + close_m
        
        # Se c'è una time preference, filtra gli orari
        pref_range = None
        if time_preference:
            pref = next((p for p in tenant["time_preferences"] if p["id"] == time_preference), None)
            if pref:
                from_h, from_m = map(int, pref["from_time"].split(":"))
                to_h, to_m = map(int, pref["to_time"].split(":"))
                pref_range = {
                    "from": from_h * 60 + from_m,
                    "to": to_h * 60 + to_m,
                }
        
        while current_minutes + service_duration <= end_minutes:
            # Salta se fuori dalla fascia preferita
            if pref_range and (current_minutes < pref_range["from"] or current_minutes >= pref_range["to"]):
                current_minutes += interval
                continue
            
            # Formatta orario
            h = current_minutes // 60
            m = current_minutes % 60
            time_str = f"{h:02d}:{m:02d}"
            
            # Verifica se lo slot è libero
            is_occupied = self._is_slot_occupied(
                slot_minutes=current_minutes,
                duration=service_duration,
                bookings=day_bookings,
            )
            
            if not is_occupied:
                slots.append(TimeSlot(time=time_str, available=True))
            
            current_minutes += interval
        
        return slots
    
    def _is_slot_occupied(
        self,
        slot_minutes: int,
        duration: int,
        bookings: list,
    ) -> bool:
        """Verifica se uno slot è occupato da una prenotazione."""
        for booking in bookings:
            b_h, b_m = map(int, booking.time.split(":"))
            booking_start = b_h * 60 + b_m
            booking_duration = getattr(booking, "duration", duration)
            booking_end = booking_start + booking_duration
            
            # Verifica sovrapposizione
            if slot_minutes < booking_end and (slot_minutes + duration) > booking_start:
                return True
        
        return False
    
    def _is_exception_closed(self, tenant: dict, date_str: str) -> bool:
        """Verifica se il giorno è chiuso per eccezione."""
        return any(
            exc["date"] == date_str and exc["type"] == "closed"
            for exc in tenant.get("exceptions", [])
        )