"""
Message Builder.

Costruisce messaggi WhatsApp interattivi (testo, bottoni, liste)
in base alla prossima azione da intraprendere.
"""

from typing import Dict, Any, List, Optional
from app.services.booking_state_service import NextAction
from app.services.availability_engine import AvailabilityResult
from app.schemas.tenant import Tenant


class MessageBuilder:
    """Costruisce messaggi WhatsApp."""
    
    def build(
        self,
        action: NextAction,
        availability: AvailabilityResult,
        tenant: Tenant,
    ) -> Dict[str, Any]:
        """
        Costruisce messaggio WhatsApp in base all'azione.
        
        Args:
            action: Prossima azione da intraprendere
            availability: Disponibilità calcolata
            tenant: Configurazione tenant
            
        Returns:
            Payload messaggio WhatsApp
        """
        if action.type == "confirm":
            return self._build_confirm_message(action)
        
        elif action.type == "ask":
            return self._build_ask_message(action, availability)
        
        elif action.type == "complete":
            return {
                "type": "text",
                "body": "Prenotazione confermata! 🎉\nTi manderò un promemoria. A presto!",
            }
        
        else:
            return {
                "type": "text",
                "body": "Come posso aiutarti?",
            }
    
    def _build_confirm_message(self, action: NextAction) -> Dict[str, Any]:
        """Costruisce messaggio di conferma con bottoni."""
        options = action.options or []
        
        if len(options) <= 3:
            # Usa bottoni (max 3)
            return {
                "type": "buttons",
                "body": action.message,
                "buttons": [
                    {"id": opt["id"], "title": opt["label"]}
                    for opt in options
                ],
            }
        
        # Usa lista per più opzioni
        return {
            "type": "list",
            "body": action.message,
            "list_button": "Scegli",
            "sections": [{
                "title": "Opzioni",
                "rows": [
                    {"id": opt["id"], "title": opt["label"]}
                    for opt in options
                ],
            }],
        }
    
    def _build_ask_message(
        self,
        action: NextAction,
        availability: AvailabilityResult,
    ) -> Dict[str, Any]:
        """Costruisce messaggio di domanda."""
        options = action.options or []
        
        if not options:
            return {
                "type": "text",
                "body": "Mi dispiace, non ci sono disponibilità al momento. Vuoi provare un'altra data?",
            }
        
        if len(options) <= 3:
            # Bottoni (WhatsApp permette max 3 bottoni)
            return {
                "type": "buttons",
                "body": action.message,
                "buttons": [
                    {"id": opt["id"], "title": opt["label"][:20]}  # max 20 chars
                    for opt in options
                ],
            }
        
        if len(options) <= 10:
            # Lista (WhatsApp permette max 10 righe per sezione)
            return {
                "type": "list",
                "body": action.message,
                "list_button": "Scegli",
                "sections": [{
                    "title": "Giorni disponibili" if action.field == "date" else "Opzioni",
                    "rows": [
                        {"id": opt["id"], "title": opt["label"]}
                        for opt in options
                    ],
                }],
            }
        
        # Più di 10 opzioni: raggruppa in sezioni
        sections = self._group_options_into_sections(options, action.field)
        return {
            "type": "list",
            "body": action.message,
            "list_button": "Scegli",
            "sections": sections,
        }
    
    def _group_options_into_sections(
        self,
        options: List[Dict[str, str]],
        field: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Raggruppa opzioni in sezioni da max 10 righe."""
        sections = []
        
        for i in range(0, len(options), 10):
            chunk = options[i:i + 10]
            section_title = (
                "Questa settimana" if i == 0 and field == "date"
                else f"Settimana {(i // 10) + 1}" if field == "date"
                else f"Opzioni {(i // 10) + 1}"
            )
            
            sections.append({
                "title": section_title,
                "rows": [
                    {"id": opt["id"], "title": opt["label"]}
                    for opt in chunk
                ],
            })
        
        return sections