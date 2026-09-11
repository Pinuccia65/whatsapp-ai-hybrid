"""
WhatsApp Service.

Gestisce l'invio di messaggi tramite WhatsApp Business Cloud API.
Supporta messaggi testo, bottoni e liste.
"""

from typing import Dict, Any, List, Optional
import httpx

from app.config import settings


class WhatsAppService:
    """Servizio per invio messaggi WhatsApp."""
    
    def __init__(self):
        self.base_url = settings.whatsapp_api_url
        self.token = settings.whatsapp_token
    
    async def send_message(
        self,
        phone_number_id: str,
        to: str,
        message: Dict[str, Any],
    ) -> None:
        """
        Invia un messaggio WhatsApp.
        
        Args:
            phone_number_id: ID del numero telefono WhatsApp
            to: Numero telefono destinatario
            message: Payload del messaggio
        """
        url = f"{self.base_url}/{phone_number_id}/messages"
        
        body = self._build_message_body(to, message)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.token}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                    timeout=10.0,
                )
                
                if response.status_code != 200:
                    error = response.json()
                    print(f"❌ WhatsApp API error: {error}")
                    raise Exception(f"WhatsApp API error: {response.status_code}")
                
                print(f"✅ Message sent to {to}")
                
        except Exception as e:
            print(f"❌ Failed to send WhatsApp message: {e}")
            raise
    
    def _build_message_body(self, to: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Costruisce il body del messaggio in formato WhatsApp API."""
        base = {
            "messaging_product": "whatsapp",
            "to": to,
        }
        
        msg_type = message.get("type", "text")
        
        # Messaggio con bottoni
        if msg_type == "buttons":
            return {
                **base,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": message["body"]},
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {
                                    "id": btn["id"],
                                    "title": btn["title"],
                                },
                            }
                            for btn in message.get("buttons", [])
                        ],
                    },
                },
            }
        
        # Messaggio con lista
        elif msg_type == "list":
            return {
                **base,
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "body": {"text": message["body"]},
                    "action": {
                        "button": message.get("list_button", "Scegli"),
                        "sections": message.get("sections", []),
                    },
                },
            }
        
        # Messaggio testo semplice
        else:
            return {
                **base,
                "type": "text",
                "text": {"body": message["body"]},
            }