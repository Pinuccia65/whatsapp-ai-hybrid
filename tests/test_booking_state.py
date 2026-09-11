"""
Test per Booking State Service.
"""

import pytest
from datetime import datetime

from app.services.booking_state_service import BookingStateService
from app.schemas.booking import BookingState
from app.services.availability_engine import AvailabilityResult, DayAvailability, TimeSlot


class TestBookingStateService:
    """Test Booking State Service."""
    
    def test_create_initial_state(self, sample_tenant):
        """Test creazione stato iniziale."""
        service = BookingStateService()
        
        extraction = {
            "intent": "create",
            "party_size": 4,
            "time_preference": "dinner",
            "date": "2026-09-12",
            "time": None,
            "service_id": None,
            "customer_name": None,
        }
        
        state = service.create_initial_state(
            phone_number="+393331234567",
            tenant_id="test_tenant_1",
            extraction=extraction,
        )
        
        assert state.phone_number == "+393331234567"
        assert state.tenant_id == "test_tenant_1"
        assert state.intent == "create"
        assert state.party_size == 4
        assert state.time_preference == "dinner"
        assert state.date == "2026-09-12"
        assert state.time is None
        assert state.status == "collecting"
    
    def test_handle_button_response(self, sample_booking_state):
        """Test gestione risposta bottone."""
        service = BookingStateService()
        
        # Risposta party_size
        state = service.handle_button_response(sample_booking_state, "party_size:4")
        assert state.party_size == 4
        
        # Risposta time_preference
        state = service.handle_button_response(state, "time_preference:dinner")
        assert state.time_preference == "dinner"
        
        # Risposta date
        state = service.handle_button_response(state, "date:2026-09-12")
        assert state.date == "2026-09-12"
        
        # Risposta time
        state = service.handle_button_response(state, "time:20:30")
        assert state.time == "20:30"
        
        # Conferma
        state = service.handle_button_response(state, "confirm:yes")
        assert state.status == "completed"
    
    def test_is_state_complete(self, sample_booking_state):
        """Test verifica stato completo."""
        service = BookingStateService()
        
        # Stato incompleto
        assert service._is_state_complete(sample_booking_state) is False
        
        # Stato completo
        complete_state = sample_booking_state.copy(update={
            "party_size": 4,
            "time_preference": "dinner",
            "date": "2026-09-12",
            "time": "20:30",
        })
        assert service._is_state_complete(complete_state) is True
    
    def test_get_next_missing_field(self, sample_booking_state):
        """Test determinazione prossimo campo mancante."""
        service = BookingStateService()
        
        # Tutti mancanti → party_size
        assert service._get_next_missing_field(sample_booking_state) == "party_size"
        
        # Party size presente → time_preference
        state = sample_booking_state.copy(update={"party_size": 4})
        assert service._get_next_missing_field(state) == "time_preference"
        
        # Time preference presente → date
        state = state.copy(update={"time_preference": "dinner"})
        assert service._get_next_missing_field(state) == "date"
        
        # Date presente → time
        state = state.copy(update={"date": "2026-09-12"})
        assert service._get_next_missing_field(state) == "time"
        
        # Tutto presente → None
        state = state.copy(update={"time": "20:30"})
        assert service._get_next_missing_field(state) is None
    
    def test_get_next_action_confirm(self, sample_tenant):
        """Test next action per stato completo."""
        service = BookingStateService()
        
        complete_state = BookingState(
            conversation_id="test",
            phone_number="+393331234567",
            tenant_id="test_tenant_1",
            intent="create",
            party_size=4,
            time_preference="dinner",
            date="2026-09-12",
            time="20:30",
            status="collecting",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        availability = AvailabilityResult(
            days=[],
            total_slots=0,
            has_availability=False,
            preferences_with_availability=[],
        )
        
        action = service.get_next_action(complete_state, sample_tenant, availability)
        
        assert action.type == "confirm"
        assert "Confermi" in action.message
        assert len(action.options) == 2