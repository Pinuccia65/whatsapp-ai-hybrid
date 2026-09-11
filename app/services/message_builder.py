"""Message Builder - costruisce messaggi WhatsApp."""

from typing import Dict, Any
from app.services.booking_state_service import NextAction


class MessageBuilder:
    def build(self, action: NextAction, availability: dict, tenant: dict) -> Dict[str, Any]:
        if action.type == "confirm":
            opts = action.options or []
            return {"type": "buttons", "body": action.message, "buttons": [{"id": o["id"], "title": o["label"]} for o in opts[:3]]}
        elif action.type == "ask":
            opts = action.options or []
            if not opts:
                return {"type": "text", "body": "Non ci sono disponibilita."}
            if len(opts) <= 3:
                return {"type": "buttons", "body": action.message, "buttons": [{"id": o["id"], "title": o["label"][:20]} for o in opts]}
            return {"type": "list", "body": action.message, "list_button": "Scegli", "sections": [{"title": "Opzioni", "rows": [{"id": o["id"], "title": o["label"]} for o in opts[:10]]}]}
        return {"type": "text", "body": "Prenotazione confermata!"}