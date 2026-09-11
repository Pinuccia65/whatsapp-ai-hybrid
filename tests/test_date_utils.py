"""
Test per utility date e orari.
"""

import pytest
from datetime import date

from app.utils.date_utils import (
    time_to_minutes,
    minutes_to_time,
    is_time_in_preference,
    format_date_it,
    format_day_short_it,
    add_days,
    generate_date_range,
    is_weekend,
    parse_date,
)


class TestTimeConversion:
    """Test conversioni orario/minuti."""
    
    def test_time_to_minutes(self):
        assert time_to_minutes("00:00") == 0
        assert time_to_minutes("01:00") == 60
        assert time_to_minutes("12:00") == 720
        assert time_to_minutes("12:30") == 750
        assert time_to_minutes("23:59") == 1439
    
    def test_minutes_to_time(self):
        assert minutes_to_time(0) == "00:00"
        assert minutes_to_time(60) == "01:00"
        assert minutes_to_time(720) == "12:00"
        assert minutes_to_time(750) == "12:30"
        assert minutes_to_time(1439) == "23:59"
    
    def test_roundtrip(self):
        """Test conversione roundtrip."""
        for time_str in ["00:00", "09:30", "12:00", "18:45", "23:59"]:
            minutes = time_to_minutes(time_str)
            result = minutes_to_time(minutes)
            assert result == time_str


class TestTimePreference:
    """Test verifica fascia oraria."""
    
    def test_time_in_preference(self):
        assert is_time_in_preference("12:00", "12:00", "14:30") is True
        assert is_time_in_preference("13:00", "12:00", "14:30") is True
        assert is_time_in_preference("14:29", "12:00", "14:30") is True
        assert is_time_in_preference("14:30", "12:00", "14:30") is False  # Limite superiore escluso
        assert is_time_in_preference("11:59", "12:00", "14:30") is False
    
    def test_evening_preference(self):
        assert is_time_in_preference("19:00", "19:00", "23:00") is True
        assert is_time_in_preference("22:30", "19:00", "23:00") is True
        assert is_time_in_preference("18:59", "19:00", "23:00") is False
        assert is_time_in_preference("23:00", "19:00", "23:00") is False


class TestDateFormatting:
    """Test formattazione date."""
    
    def test_format_date_it(self):
        d = date(2026, 9, 12)
        assert format_date_it(d) == "12 Settembre 2026"
        
        d = date(2026, 1, 1)
        assert format_date_it(d) == "1 Gennaio 2026"
    
    def test_format_day_short_it(self):
        # 12 Settembre 2026 è sabato
        d = date(2026, 9, 12)
        assert format_day_short_it(d) == "Sab 12"
        
        # 13 Settembre 2026 è domenica
        d = date(2026, 9, 13)
        assert format_day_short_it(d) == "Dom 13"


class TestDateOperations:
    """Test operazioni su date."""
    
    def test_add_days(self):
        d = date(2026, 9, 12)
        assert add_days(d, 1) == date(2026, 9, 13)
        assert add_days(d, 7) == date(2026, 9, 19)
        assert add_days(d, 30) == date(2026, 10, 12)
    
    def test_generate_date_range(self):
        start = date(2026, 9, 12)
        end = date(2026, 9, 15)
        
        dates = generate_date_range(start, end)
        
        assert len(dates) == 4
        assert dates[0] == start
        assert dates[-1] == end
    
    def test_is_weekend(self):
        # Sabato
        assert is_weekend(date(2026, 9, 12)) is True
        # Domenica
        assert is_weekend(date(2026, 9, 13)) is True
        # Lunedì
        assert is_weekend(date(2026, 9, 14)) is False
    
    def test_parse_date(self):
        d = parse_date("2026-09-12")
        assert d == date(2026, 9, 12)
        
        d = parse_date("2026-01-01")
        assert d == date(2026, 1, 1)