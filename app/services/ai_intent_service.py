"""AI Intent Service - OpenAI integration."""

import json
from typing import Dict, Any
from openai import AsyncOpenAI
from datetime import datetime

from app.config import settings
from app.schemas.booking import BookingState


class AIIntentService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def extract_intent(self, message: str, tenant: dict) -> Dict[str, Any]:
        time_prefs = "\n".join([
            f'- "{p["pref_key"]}": {p["label"]} ({p["from_time"]} - {p["to_time"]})'
            for p in tenant.get("time_preferences", [])
        ])
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        system_prompt = f"""Estrai parametri da messaggio WhatsApp per prenotazione.
Rispondi SOLO con JSON:
{{"intent": "create"|"move"|"cancel"|null, "party_size": number|null, "time_preference": string|null, "date": "YYYY-MM-DD"|null, "time": "HH:mm"|null}}

Oggi: {today}
Fasce: {time_prefs}

Regole: "prenotare"=create, "spostare"=move, "cancellare"=cancel. Calcola date relative a oggi."""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": message}],
                temperature=settings.openai_temperature,
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content or "{}")
        except Exception as e:
            print(f"AI error: {e}")
            return {"intent": None, "party_size": None, "time_preference": None, "date": None, "time": None}
    
    async def extract_update(self, message: str, state: BookingState, tenant: dict) -> Dict[str, Any]:
        missing = [f for f in ["party_size", "time_preference", "date", "time"] if not getattr(state, f)]
        prompt = f"Mancano: {', '.join(missing)}. Stato: intent={state.intent}, party_size={state.party_size}, time_preference={state.time_preference}, date={state.date}, time={state.time}. Aggiorna solo campi determinabili. JSON."
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "system", "content": prompt}, {"role": "user", "content": message}],
                temperature=0,
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content or "{}")
        except Exception:
            return {}