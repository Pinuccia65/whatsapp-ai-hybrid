"""
Test per AI Intent Service.
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.services.ai_intent_service import AIIntentService


class TestAIIntentService:
    """Test AI Intent Service."""
    
    def test_empty_extraction(self):
        """Test estrazione vuota."""
        service = AIIntentService()
        result = service._empty_extraction()
        
        assert result["intent"] is None
        assert result["party_size"] is None
        assert result["time_preference"] is None
        assert result["date"] is None
        assert result["time"] is None
    
    def test_get_missing_fields(self, sample_booking_state):
        """Test determinazione campi mancanti."""
        service = AIIntentService()
        
        missing = service._get_missing_fields(sample_booking_state)
        
        assert "party_size" in missing
        assert "time_preference" in missing
        assert "date" in missing
        assert "time" in missing
        
        # Con alcuni campi compilati
        state = sample_booking_state.copy(update={"party_size": 4})
        missing = service._get_missing_fields(state)
        
        assert "party_size" not in missing
        assert len(missing) == 3
    
    def test_build_system_prompt(self, sample_tenant):
        """Test costruzione system prompt."""
        service = AIIntentService()
        
        prompt = service._build_system_prompt(sample_tenant)
        
        assert "prenotare" in prompt
        assert "spostare" in prompt
        assert "cancellare" in prompt
        assert "Pranzo" in prompt
        assert "Cena" in prompt
        assert "JSON" in prompt
    
    @pytest.mark.asyncio
    async def test_extract_intent_mock(self, sample_tenant):
        """Test estrazione intent con mock OpenAI."""
        service = AIIntentService()
        
        # Mock della risposta OpenAI
        mock_response = AsyncMock()
        mock_response.choices = [
            AsyncMock(
                message=AsyncMock(
                    content='{"intent": "create", "party_size": 4, "time_preference": "dinner", "date": "2026-09-12", "time": null, "service_id": null, "customer_name": null}'
                )
            )
        ]
        
        with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
            result = await service.extract_intent("Vorrei prenotare per 4 sabato sera", sample_tenant)
            
            assert result["intent"] == "create"
            assert result["party_size"] == 4
            assert result["time_preference"] == "dinner"