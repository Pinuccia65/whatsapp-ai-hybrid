"""WhatsApp Controller - Orchestratore principale."""

from typing import Optional
from app.schemas.whatsapp import WhatsAppWebhookPayload, WhatsAppMessage
from app.schemas.booking import BookingState
from app.services.ai_intent_service import AIIntentService
from app.services.booking_state_service import BookingStateService
from app.services.availability_engine import AvailabilityEngine
from app.services.tenant_service import TenantService
from app.services.message_builder import MessageBuilder
from app.services.whatsapp_service import WhatsAppService
from app.services.booking_service import BookingService


class WhatsAppController:
    def __init__(self):
        self.ai_service = AIIntentService()
        self.state_service = BookingStateService()
        self.availability_engine = AvailabilityEngine()
        self.tenant_service = TenantService()
        self.message_builder = MessageBuilder()
        self.whatsapp_service = WhatsAppService()
        self.booking_service = BookingService()
    
    async def handle_incoming_message(self, payload: WhatsAppWebhookPayload) -> None:
        # 1. Estrai messaggio
        message = self._extract_message(payload)
        if not message:
            return
        
        phone_number = message.from_
        phone_number_id = payload.entry[0].changes[0].value.metadata.phone_number_id
        
        # 2. Trova tenant
        tenant = await self.tenant_service.get_tenant_by_whatsapp_id(phone_number_id)
        if not tenant:
            return
        
        # 3. Stato conversazione (da Supabase, non Redis!)
        state = await self.state_service.get_state(phone_number, tenant["id"])
        message_text = self._extract_message_text(message)
        button_payload = self._extract_button_payload(message)
        
        if not state:
            extraction = await self.ai_service.extract_intent(message_text, tenant)
            state = self.state_service.create_initial_state(phone_number, tenant["id"], extraction)
        elif button_payload:
            state = self.state_service.handle_button_response(state, button_payload)
        else:
            update = await self.ai_service.extract_update(message_text, state, tenant)
            state = self.state_service.update_state(state, update)
        
        # 4. Disponibilità
        availability = await self.availability_engine.calculate(
            tenant_id=tenant["id"],
            time_preference=state.time_preference,
            date=state.date,
            party_size=state.party_size,
        )
        
        # 5. Prossima azione
        next_action = self.state_service.get_next_action(state, tenant, availability)
        
        # 6. Invia messaggio
        wa_message = self.message_builder.build(next_action, availability, tenant)
        await self.whatsapp_service.send_message(phone_number_id, phone_number, wa_message)
        
        # 7. Se confermato, crea prenotazione
        if state.status == "completed":
            await self.booking_service.create_from_state(state)
        
        # 8. Salva stato in Supabase
        await self.state_service.save_state(state)
    
    def _extract_message(self, payload: WhatsAppWebhookPayload) -> Optional[WhatsAppMessage]:
        try:
            msgs = payload.entry[0].changes[0].value.messages
            return msgs[0] if msgs else None
        except (IndexError, AttributeError):
            return None
    
    def _extract_message_text(self, message: WhatsAppMessage) -> str:
        if message.type == "text" and message.text:
            return message.text.body
        if message.type == "interactive" and message.interactive:
            if message.interactive.button_reply:
                return message.interactive.button_reply.title
            if message.interactive.list_reply:
                return message.interactive.list_reply.title
        return ""
    
    def _extract_button_payload(self, message: WhatsAppMessage) -> Optional[str]:
        if message.type == "interactive" and message.interactive:
            if message.interactive.button_reply:
                return message.interactive.button_reply.id
            if message.interactive.list_reply:
                return message.interactive.list_reply.id
        return None