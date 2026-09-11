"""Database models (MongoDB/Beanie)."""

from app.models.tenant import TenantModel, Tenant
from app.models.booking import BookingModel, Booking

__all__ = ["TenantModel", "Tenant", "BookingModel", "Booking"]