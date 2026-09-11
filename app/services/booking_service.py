"""
Booking Service.

Gestisce le operazioni CRUD sulle prenotazioni.
"""

from typing import Optional, List
from datetime import date, datetime

from app.models.booking import BookingModel, Booking
from app.schemas.booking import BookingCreate, BookingStatus, BookingState


class BookingService:
    """Servizio per gestione prenotazioni."""
    
    async def list_bookings(
        self,
        tenant_id: str,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        status: Optional[BookingStatus] = None,
    ) -> List[Booking]:
        """Lista prenotazioni con filtri."""
        query = BookingModel.find(BookingModel.tenant_id == tenant_id)
        
        if date_from:
            query = query.find(BookingModel.date >= date_from.isoformat())
        if date_to:
            query = query.find(BookingModel.date <= date_to.isoformat())
        if status:
            query = query.find(BookingModel.status == status)
        
        bookings = await query.sort(BookingModel.date, BookingModel.time).to_list()
        return [b.to_dict() for b in bookings]
    
    async def get_booking(self, booking_id: str) -> Optional[Booking]:
        """Ottieni prenotazione per ID."""
        booking = await BookingModel.find_one(BookingModel.id == booking_id)
        return booking.to_dict() if booking else None
    
    async def create_booking(self, data: BookingCreate) -> Booking:
        """Crea una nuova prenotazione."""
        booking = BookingModel(
            tenant_id=data.tenant_id,
            phone_number=data.phone_number,
            customer_name=data.customer_name,
            intent="create",
            party_size=data.party_size,
            date=data.date,
            time=data.time,
            service_id=data.service_id,
            status="confirmed",
            confirmed_at=datetime.utcnow(),
        )
        await booking.insert()
        return booking.to_dict()
    
    async def create_from_state(self, state: BookingState) -> Booking:
        """Crea prenotazione da stato conversazione."""
        booking = BookingModel(
            tenant_id=state.tenant_id,
            phone_number=state.phone_number,
            customer_name=state.customer_name,
            intent=state.intent or "create",
            party_size=state.party_size or 1,
            date=state.date or "",
            time=state.time or "",
            time_preference=state.time_preference,
            service_id=state.service_id,
            status="confirmed",
            confirmed_at=datetime.utcnow(),
        )
        await booking.insert()
        return booking.to_dict()
    
    async def update_status(self, booking_id: str, status: BookingStatus) -> Optional[Booking]:
        """Aggiorna stato prenotazione."""
        booking = await BookingModel.find_one(BookingModel.id == booking_id)
        if not booking:
            return None
        
        booking.status = status
        booking.updated_at = datetime.utcnow()
        
        if status == "confirmed":
            booking.confirmed_at = datetime.utcnow()
        
        await booking.save()
        return booking.to_dict()
    
    async def cancel_booking(self, booking_id: str) -> None:
        """Cancella una prenotazione."""
        booking = await BookingModel.find_one(BookingModel.id == booking_id)
        if booking:
            booking.status = "cancelled"
            booking.updated_at = datetime.utcnow()
            await booking.save()