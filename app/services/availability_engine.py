"""Availability Engine - usa funzione SQL di Supabase."""

from datetime import datetime, timedelta
from typing import Optional

from app.utils.supabase_client import get_supabase

DAYS_SHORT = ["Dom", "Lun", "Mar", "Mer", "Gio", "Ven", "Sab"]


class AvailabilityEngine:
    async def calculate(self, tenant_id: str, time_preference: str = None, date: str = None, party_size: int = None) -> dict:
        supabase = get_supabase()
        
        # Carica tenant
        t_resp = supabase.table("tenants").select("*, time_preferences(*), services(*), opening_hours(*)").eq("id", tenant_id).execute()
        if not t_resp.data:
            raise ValueError("Tenant not found")
        
        tenant = t_resp.data[0]
        max_days = tenant.get("max_advance_days", 30)
        
        start = datetime.now().date()
        end = start + timedelta(days=max_days)
        
        days = []
        prefs_with_avail = set()
        current = start
        
        while current <= end:
            try:
                slots_resp = supabase.rpc("get_available_slots", {
                    "p_tenant_id": tenant_id,
                    "p_date": current.isoformat(),
                    "p_time_preference": time_preference,
                    "p_party_size": party_size,
                }).execute()
                
                slots = slots_resp.data or []
                if slots:
                    dow = (current.weekday() + 1) % 7
                    days.append({
                        "date": current.isoformat(),
                        "day_of_week": dow,
                        "day_label": f"{DAYS_SHORT[dow]} {current.day}",
                        "slots": [{"time": s["slot_time"]} for s in slots],
                        "slot_count": len(slots),
                    })
            except Exception as e:
                print(f"Error for {current}: {e}")
            
            current += timedelta(days=1)
        
        return {
            "days": days,
            "total_slots": sum(d["slot_count"] for d in days),
            "has_availability": len(days) > 0,
            "preferences_with_availability": list(prefs_with_avail),
        }