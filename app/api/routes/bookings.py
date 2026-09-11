"""Bookings Routes."""

from typing import Optional, List
from datetime import date
from fastapi import APIRouter, HTTPException, Query

from app.schemas.booking import Booking, BookingCreate
from app.services.booking_service import BookingService

router = APIRouter()
service = BookingService()


@router.get("/", response_model=List[Booking])
async def list_bookings(
    tenant_id: str = Query(...),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
):
    return await service.list_bookings(tenant_id, date_from, date_to, status)


@router.post("/", response_model=Booking, status_code=201)
async def create_booking(booking: BookingCreate):
    try:
        return await service.create_booking(booking)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{booking_id}", response_model=Booking)
async def get_booking(booking_id: str):
    booking = await service.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Not found")
    return booking


@router.patch("/{booking_id}/status", response_model=Booking)
async def update_status(booking_id: str, status: str):
    booking = await service.update_status(booking_id, status)
    if not booking:
        raise HTTPException(status_code=404, detail="Not found")
    return booking


@router.delete("/{booking_id}", status_code=204)
async def cancel_booking(booking_id: str):
    await service.cancel_booking(booking_id)