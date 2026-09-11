"""WhatsApp Service - invio messaggi via API."""

from typing import Dict, Any
import httpx
from app.config import settings


class WhatsAppService:
    def __init__(self):
        self.base_url = settings.whatsapp_api_url
        self.token = settings.whatsapp_token
    
    async def send_message(self, phone_number_id: str, to: str, message: Dict[str, Any]) -> None:
        url = f"{self.base_url}/{phone_number_id}/messages"
        body = self._build_body(to, message)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }, json=body, timeout=10.0)
            
            if response.status_code != 200:
                raise Exception(f"WhatsApp error: {response.status_code}")
            print(f"Message sent to {to}")
    
    def _build_body(self, to: str, message: Dict[str, Any]) -> Dict[str, Any]:
        base = {"messaging_product": "whatsapp", "to": to}
        t = message.get("type", "text")
        
        if t == "buttons":
            return {**base, "type": "interactive", "interactive": {
                "type": "button", "body": {"text": message["body"]},
                "action": {"buttons": [{"type": "reply", "reply": {"id": b["id"], "title": b["title"]}} for b in message.get("buttons", [])]},
            }}
        elif t == "list":
            return {**base, "type": "interactive", "interactive": {
                "type": "list", "body": {"text": message["body"]},
                "action": {"button": message.get("list_button", "Scegli"), "sections": message.get("sections", [])},
            }}
        return {**base, "type": "text", "text": {"body": message["body"]}}