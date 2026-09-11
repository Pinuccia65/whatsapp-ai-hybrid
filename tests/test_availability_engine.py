"""
Test per Availability Engine.
"""

import pytest
from datetime import datetime, timedelta

from app.services.availability_engine import AvailabilityEngine
from app.utils.date_utils import time_to_minutes, is_time_in_preference


class TestTimeUtils:
    """Test utility date/orari."""
    
    def test_time_to_minutes(self):
        assert time_to_minutes("09:00") == 540
        assert time_to_minutes("12:30") == 750
        assert time_to_minutes("00:00") == 0
        assert time_to_minutes("23:59") == 1439
    
    def test_is_time_in_preference(self):
        assert is_time_in_preference("12:00", "12:00", "14:30") is True
        assert is_time_in_preference("13:30", "12:00", "14:30") is True
        assert is_time_in_preference("14:30", "12:00", "14:30") is False
        assert is_time_in_preference("11:59", "12:00", "14:30") is False
        assert is_time_in_preference("19:30", "19:00", "23:00") is True
        assert is_time_in_preference("18:59", "19:00", "23:00") is False


class TestAvailabilityEngine:
    """Test Availability Engine."""
    
    @pytest.mark.asyncio
    async def test_calculate_basic(self, sample_tenant):
        """Test calcolo base disponibilità."""
        engine = AvailabilityEngine()
        
        # Mock del database - in test reali si userebbe un DB di test
        # Qui verifichiamo solo la logica di calcolo slot
        slots = engine._calculate_day_slots(
            opening_hours={"open": "19:00", "close": "23:00", "day_of_week": 6},
            tenant=sample_tenant,
            day_bookings=[],
            time_preference="dinner",
            party_size=4,
        )
        
        # Verifica che ci siano slot
        assert len(slots) > 0
        
        # Verifica che tutti gli slot siano nella fascia dinner
        for slot in slots:
            assert is_time_in_preference(slot.time, "19:00", "23:00")
    
    def test_slot_occupied(self):
        """Test verifica slot occupato."""
        engine = AvailabilityEngine()
        
        bookings = [
            {"time": "20:00", "duration": 90}
        ]
        
        # Slot alle 19:00 - libero
        assert engine._is_slot_occupied(
            slot_minutes=time_to_minutes("19:00"),
            duration=90,
            bookings=bookings,
        ) is False
        
        # Slot alle 20:00 - occupato
        assert engine._is_slot_occupied(
            slot_minutes=time_to_minutes("20:00"),
            duration=90,
            bookings=bookings,
        ) is True
        
        # Slot alle 21:30 - occupato (sovrapposizione)
        assert engine._is_slot_occupied(
            slot_minutes=time_to_minutes("21:30"),
            duration=90,
            bookings=bookings,
        ) is True
        
        # Slot alle 22:00 - libero
        assert engine._is_slot_occupied(
            slot_minutes=time_to_minutes("22:00"),
            duration=90,
            bookings=bookings,
        ) is False