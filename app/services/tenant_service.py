"""Tenant Service - Supabase."""

from typing import Optional, List
from app.utils.supabase_client import get_supabase


class TenantService:
    async def list_tenants(self) -> List[dict]:
        supabase = get_supabase()
        r = supabase.table("tenants").select("*, time_preferences(*), services(*), opening_hours(*)").execute()
        return r.data or []
    
    async def get_tenant(self, tenant_id: str) -> Optional[dict]:
        supabase = get_supabase()
        r = supabase.table("tenants").select("*, time_preferences(*), services(*), opening_hours(*)").eq("id", tenant_id).execute()
        return r.data[0] if r.data else None
    
    async def get_tenant_by_whatsapp_id(self, phone_id: str) -> Optional[dict]:
        supabase = get_supabase()
        r = supabase.table("tenants").select("*, time_preferences(*), services(*), opening_hours(*)").eq("whatsapp_phone_number_id", phone_id).execute()
        return r.data[0] if r.data else None
    
    async def create_tenant(self, data: dict) -> dict:
        supabase = get_supabase()
        
        # Inserisci tenant
        t = supabase.table("tenants").insert({
            "name": data["name"], "type": data["type"],
            "whatsapp_phone_number_id": data["whatsapp_phone_number_id"],
            "capacity": data.get("capacity", 20),
        }).execute().data[0]
        
        tid = t["id"]
        
        # Fasce orarie
        for p in data.get("time_preferences", []):
            supabase.table("time_preferences").insert({
                "tenant_id": tid, "pref_key": p["id"], "label": p["label"],
                "from_time": p["from"], "to_time": p["to"],
            }).execute()
        
        # Servizi
        for s in data.get("services", []):
            supabase.table("services").insert({
                "tenant_id": tid, "service_key": s["id"],
                "name": s["name"], "duration_minutes": s["duration_minutes"],
            }).execute()
        
        # Orari
        for oh in data.get("opening_hours", []):
            supabase.table("opening_hours").insert({
                "tenant_id": tid, "day_of_week": oh["day_of_week"],
                "open_time": oh["open"], "close_time": oh["close"],
            }).execute()
        
        return await self.get_tenant(tid)
    
    async def update_tenant(self, tenant_id: str, data: dict) -> Optional[dict]:
        supabase = get_supabase()
        if "name" in data or "capacity" in data:
            updates = {}
            if "name" in data: updates["name"] = data["name"]
            if "capacity" in data: updates["capacity"] = data["capacity"]
            supabase.table("tenants").update(updates).eq("id", tenant_id).execute()
        return await self.get_tenant(tenant_id)