"""WhatsApp Webhook Routes."""

from fastapi import APIRouter, HTTPException, Query
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
    if hub_mode == "subscribe" and hub_token == settings.whatsapp_verify_token:
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Invalid verify token")


@router.post("/whatsapp")
async def receive_webhook(payload: WhatsAppWebhookPayload):
    try:
        await controller.handle_incoming_message(payload)
        return {"status": "ok"}
    except Exception as e:
        print(f"Error handling webhook: {e}")
        return {"status": "error"}