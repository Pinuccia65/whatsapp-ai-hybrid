"""
Date and time utilities.

Funzioni helper per manipolazione date, orari e slot temporali.
"""

from datetime import datetime, timedelta, date
from typing import List


def time_to_minutes(time_str: str) -> int:
    """
    Converte orario HH:mm in minuti da mezzanotte.
    
    Args:
        time_str: Orario in formato HH:mm
        
    Returns:
        Minuti da mezzanotte
    """
    h, m = map(int, time_str.split(":"))
    return h * 60 + m


def minutes_to_time(minutes: int) -> str:
    """
    Converte minuti da mezzanotte in orario HH:mm.
    
    Args:
        minutes: Minuti da mezzanotte
        
    Returns:
        Orario in formato HH:mm
    """
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def is_time_in_preference(time: str, pref_from: str, pref_to: str) -> bool:
    """
    Verifica se un orario rientra in una fascia oraria.
    
    Args:
        time: Orario da verificare (HH:mm)
        pref_from: Inizio fascia (HH:mm)
        pref_to: Fine fascia (HH:mm)
        
    Returns:
        True se l'orario è nella fascia
    """
    time_min = time_to_minutes(time)
    from_min = time_to_minutes(pref_from)
    to_min = time_to_minutes(pref_to)
    
    return from_min <= time_min < to_min


def format_date_it(date_obj: date) -> str:
    """
    Formatta data in italiano.
    
    Args:
        date_obj: Oggetto date
        
    Returns:
        Stringa formattata (es: "12 Settembre 2026")
    """
    months = [
        "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
        "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
    ]
    
    return f"{date_obj.day} {months[date_obj.month - 1]} {date_obj.year}"


def format_day_short_it(date_obj: date) -> str:
    """
    Formatta giorno in italiano breve.
    
    Args:
        date_obj: Oggetto date
        
    Returns:
        Stringa formattata (es: "Sab 12")
    """
    days = ["Dom", "Lun", "Mar", "Mer", "Gio", "Ven", "Sab"]
    return f"{days[date_obj.weekday()]} {date_obj.day}"


def add_days(date_obj: date, days: int) -> date:
    """
    Aggiunge giorni a una data.
    
    Args:
        date_obj: Data di partenza
        days: Numero giorni da aggiungere
        
    Returns:
        Nuova data
    """
    return date_obj + timedelta(days=days)


def generate_date_range(start: date, end: date) -> List[date]:
    """
    Genera lista di date tra start e end (inclusi).
    
    Args:
        start: Data inizio
        end: Data fine
        
    Returns:
        Lista di date
    """
    dates = []
    current = start
    
    while current <= end:
        dates.append(current)
        current = add_days(current, 1)
    
    return dates


def is_weekend(date_obj: date) -> bool:
    """
    Verifica se una data è nel weekend.
    
    Args:
        date_obj: Data da verificare
        
    Returns:
        True se sabato o domenica
    """
    return date_obj.weekday() >= 5  # 5 = sabato, 6 = domenica


def parse_date(date_str: str) -> date:
    """
    Parsa stringa data in oggetto date.
    
    Args:
        date_str: Stringa in formato YYYY-MM-DD
        
    Returns:
        Oggetto date
    """
    return datetime.strptime(date_str, "%Y-%m-%d").date()