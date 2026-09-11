"""
Pytest configuration and fixtures.
"""

import pytest
from datetime import datetime

from app.schemas.tenant import Tenant, TimePreference, Service, OpeningHours, BookingRules
from app.schemas.booking import BookingState


@pytest.fixture
def sample_tenant():
    """Tenant di esempio per test."""
    return {
        "id": "test_tenant_1",
        "name": "Ristorante Test",
        "type": "restaurant",
        "time_preferences": [
            {"id": "lunch", "label": "Pranzo", "from": "12:00", "to": "14:30"},
            {"id": "dinner", "label": "Cena", "from": "19:00", "to": "23:00"},
        ],
        "services": [
            {"id": "table", "name": "Tavolo", "duration_minutes": 90},
        ],
        "opening_hours": [
            {"day_of_week": 0, "open": "12:00", "close": "14:30"},  # Domenica
            {"day_of_week": 1, "open": "12:00", "close": "14:30"},  # Lunedì
            {"day_of_week": 2, "open": "12:00", "close": "14:30"},  # Martedì
            {"day_of_week": 3, "open": "12:00", "close": "14:30"},  # Mercoledì
            {"day_of_week": 4, "open": "12:00", "close": "14:30"},  # Giovedì
            {"day_of_week": 5, "open": "12:00", "close": "14:30"},  # Venerdì
            {"day_of_week": 6, "open": "12:00", "close": "23:00"},  # Sabato
        ],
        "booking_rules": {
            "min_advance_hours": 2,
            "max_advance_days": 30,
            "slot_interval_minutes": 30,
            "max_party_size": 20,
            "min_party_size": 1,
        },
        "whatsapp_phone_number_id": "test_phone_123",
        "capacity": 60,
        "exceptions": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_booking_state():
    """Stato conversazione di esempio."""
    return BookingState(
        conversation_id="test_conv_1",
        phone_number="+393331234567",
        tenant_id="test_tenant_1",
        intent="create",
        party_size=None,
        time_preference=None,
        date=None,
        time=None,
        status="collecting",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )