"""
AI Intent Service.

Utilizza OpenAI per estrarre intent e parametri dai messaggi
degli utenti in linguaggio naturale.
"""

import json
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from datetime import datetime, timedelta

from app.config import settings
from app.schemas.tenant import Tenant
from app.schemas.booking import BookingState, BookingIntent


class AIIntentService:
    """Servizio per estrazione intent con LLM."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
    
    async def extract_intent(self, message: str, tenant: Tenant) -> Dict[str, Any]:
        """
        Estrae intent e parametri dal primo messaggio.
        
        Args:
            message: Testo del messaggio utente
            tenant: Configurazione del tenant
            
        Returns:
            Dizionario con intent e parametri estratti
        """
        system_prompt = self._build_system_prompt(tenant)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            if not content:
                return self._empty_extraction()
            
            return json.loads(content)
            
        except Exception as e:
            print(f"❌ AI extraction error: {e}")
            return self._empty_extraction()
    
    async def extract_update(
        self,
        message: str,
        state: BookingState,
        tenant: Tenant,
    ) -> Dict[str, Any]:
        """
        Estrae aggiornamenti dallo stato corrente.
        
        Usato per messaggi successivi al primo, quando lo stato
        è già parzialmente popolato.
        """
        system_prompt = self._build_update_prompt(state, tenant)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            if not content:
                return {}
            
            return json.loads(content)
            
        except Exception as e:
            print(f"❌ AI update error: {e}")
            return {}
    
    def _build_system_prompt(self, tenant: Tenant) -> str:
        """Costruisce il system prompt per l'estrazione iniziale."""
        time_prefs = "\n".join([
            f'- "{p.id}": {p.label} ({p.from_time} - {p.to_time})'
            for p in tenant.time_preferences
        ])
        
        services = "\n".join([
            f'- "{s.id}": {s.name} ({s.duration_minutes} min)'
            for s in tenant.services
        ])
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        return f"""Sei un assistente che estrae informazioni da messaggi WhatsApp per un sistema di prenotazione.

Analizza il messaggio dell'utente ed estrai i seguenti parametri in formato JSON:

{{
  "intent": "create" | "move" | "cancel" | null,
  "party_size": number | null,
  "time_preference": string | null,
  "date": "YYYY-MM-DD" | null,
  "time": "HH:mm" | null,
  "service_id": string | null,
  "customer_name": string | null
}}

Oggi è {today}.

Fasce orarie disponibili:
{time_prefs}

Servizi disponibili:
{services}

Regole:
- Se l'utente dice "prenotare", "prenoto", "vorrei un tavolo" → intent = "create"
- Se l'utente dice "spostare", "cambiare", "rimandare" → intent = "move"
- Se l'utente dice "cancellare", "annullare" → intent = "cancel"
- Per la data, calcola il giorno della settimana menzionato rispetto a oggi ({today})
- Se non riesci a estrarre un campo, metti null
- Rispondi SOLO con JSON valido, senza testo aggiuntivo"""
    
    def _build_update_prompt(self, state: BookingState, tenant: Tenant) -> str:
        """Costruisce il system prompt per aggiornamenti."""
        missing = self._get_missing_fields(state)
        
        return f"""L'utente sta completando una prenotazione. Mancano questi dati: {', '.join(missing)}.

Analizza il messaggio e aggiorna SOLO i campi che riesci a determinare.
Rispondi in JSON con solo i campi aggiornati.

Stato attuale:
- intent: {state.intent}
- party_size: {state.party_size}
- time_preference: {state.time_preference}
- date: {state.date}
- time: {state.time}

Rispondi SOLO con JSON valido."""
    
    def _get_missing_fields(self, state: BookingState) -> list[str]:
        """Restituisce lista dei campi mancanti."""
        missing = []
        if not state.party_size:
            missing.append("party_size")
        if not state.time_preference:
            missing.append("time_preference")
        if not state.date:
            missing.append("date")
        if not state.time:
            missing.append("time")
        return missing
    
    def _empty_extraction(self) -> Dict[str, Any]:
        """Restituisce estrazione vuota."""
        return {
            "intent": None,
            "party_size": None,
            "time_preference": None,
            "date": None,
            "time": None,
            "service_id": None,
            "customer_name": None,
        }