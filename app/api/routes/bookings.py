"""
Bookings Routes.

Endpoint per gestire le prenotazioni:
- Lista prenotazioni con filtri
- Crea nuova prenotazione
- Aggiorna stato
- Cancella prenotazione
"""

from typing import Optional, List
from datetime import date
from fastapi import APIRouter, HTTPException, Query

from app.schemas.booking import Booking, BookingCreate, BookingStatus
from app.services.booking_service import BookingService

router = APIRouter()
service = BookingService()


@router.get("/", response_model=List[Booking])
async def list_bookings(
    tenant_id: str = Query(..., description="ID del tenant"),
    date_from: Optional[date] = Query(None, description="Data inizio"),
    date_to: Optional[date] = Query(None, description="Data fine"),
    status: Optional[BookingStatus] = Query(None, description="Filtra per stato"),
):
    """Lista prenotazioni con filtri opzionali."""
    try:
        bookings = await service.list_bookings(
            tenant_id=tenant_id,
            date_from=date_from,
            date_to=date_to,
            status=status,
        )
        return bookings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Booking, status_code=201)
async def create_booking(booking: BookingCreate):
    """Crea una nuova prenotazione."""
    try:
        created = await service.create_booking(booking)
        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{booking_id}", response_model=Booking)
async def get_booking(booking_id: str):
    """Ottieni una prenotazione per ID."""
    booking = await service.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.patch("/{booking_id}/status", response_model=Booking)
async def update_booking_status(
    booking_id: str,
    status: BookingStatus,
):
    """Aggiorna lo stato di una prenotazione."""
    try:
        booking = await service.update_status(booking_id, status)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{booking_id}", status_code=204)
async def cancel_booking(booking_id: str):
    """Cancella una prenotazione."""
    try:
        await service.cancel_booking(booking_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))