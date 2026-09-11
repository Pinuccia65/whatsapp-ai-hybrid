"""
WhatsApp Webhook Routes.

Gestisce la verifica del webhook (GET) e la ricezione
dei messaggi (POST) da WhatsApp Business API.
"""

from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse

from app.config import settings
from app.services.whatsapp_controller import WhatsAppController
from app.schemas.whatsapp import WhatsAppWebhookPayload

router = APIRouter()
controller = WhatsAppController()


@router.get("/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """
    Verifica webhook richiesta da WhatsApp.
    
    WhatsApp invia una GET con hub.mode, hub.verify_token, hub.challenge.
    Se il token corrisponde, restituisce il challenge.
    """
    if hub_mode == "subscribe" and hub_token == settings.whatsapp_verify_token:
        print("✅ Webhook verified")
        return PlainTextResponse(hub_challenge)
    
    raise HTTPException(status_code=403, detail="Invalid verify token")


@router.post("/whatsapp")
async def receive_webhook(payload: WhatsAppWebhookPayload):
    """
    Riceve messaggi da WhatsApp.
    
    WhatsApp invia POST con il payload contenente i messaggi.
    Elaboriamo il messaggio e rispondiamo all'utente.
    """
    try:
        await controller.handle_incoming_message(payload)
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ Error handling webhook: {e}")
        # Restituiamo comunque 200 per evitare retry da WhatsApp
        return {"status": "error", "message": str(e)}