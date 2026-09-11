"""
WhatsApp Controller.

Orchestratore principale del flusso:
1. Riceve messaggio WhatsApp
2. Estrae intent con AI
3. Gestisce stato conversazione
4. Calcola disponibilità
5. Costruisce e invia risposta
"""

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
    """Controller principale che orchestra il flusso di prenotazione."""
    
    def __init__(self):
        self.ai_service = AIIntentService()
        self.state_service = BookingStateService()
        self.availability_engine = AvailabilityEngine()
        self.tenant_service = TenantService()
        self.message_builder = MessageBuilder()
        self.whatsapp_service = WhatsAppService()
        self.booking_service = BookingService()
    
    async def handle_incoming_message(self, payload: WhatsAppWebhookPayload) -> None:
        """
        Gestisce un messaggio in arrivo da WhatsApp.
        
        Questo è il punto di ingresso principale per ogni messaggio.
        """
        # 1. Estrai messaggio dal payload
        message = self._extract_message(payload)
        if not message:
            print("⚠️ No message found in payload")
            return
        
        phone_number = message.from_
        phone_number_id = self._extract_phone_number_id(payload)
        
        # 2. Trova il tenant
        tenant = await self.tenant_service.get_tenant_by_whatsapp_id(phone_number_id)
        if not tenant:
            print(f"❌ Tenant not found for phone number ID: {phone_number_id}")
            return
        
        # 3. Recupera o crea stato conversazione
        state = await self.state_service.get_state(phone_number, tenant.id)
        
        message_text = self._extract_message_text(message)
        button_payload = self._extract_button_payload(message)
        
        if not state:
            # Primo messaggio: estrai intent con AI
            extraction = await self.ai_service.extract_intent(message_text, tenant)
            state = self.state_service.create_initial_state(
                phone_number=phone_number,
                tenant_id=tenant.id,
                extraction=extraction,
            )
        elif button_payload:
            # L'utente ha premuto un bottone
            state = self.state_service.handle_button_response(state, button_payload)
        else:
            # Messaggio testuale successivo
            update = await self.ai_service.extract_update(message_text, state, tenant)
            state = self.state_service.update_state(state, update)
        
        # 4. Calcola disponibilità
        availability = await self.availability_engine.calculate(
            tenant_id=tenant.id,
            time_preference=state.time_preference,
            date=state.date,
            party_size=state.party_size,
        )
        
        # 5. Determina prossima azione
        next_action = self.state_service.get_next_action(state, tenant, availability)
        
        # 6. Costruisci messaggio WhatsApp
        wa_message = self.message_builder.build(next_action, availability, tenant)
        
        # 7. Invia messaggio
        await self.whatsapp_service.send_message(
            phone_number_id=phone_number_id,
            to=phone_number,
            message=wa_message,
        )
        
        # 8. Se stato completo e confermato, crea prenotazione
        if state.status == "completed":
            await self.booking_service.create_from_state(state)
        
        # 9. Salva stato aggiornato
        await self.state_service.save_state(state)
    
    def _extract_message(self, payload: WhatsAppWebhookPayload) -> Optional[WhatsAppMessage]:
        """Estrae il primo messaggio dal payload webhook."""
        try:
            messages = payload.entry[0].changes[0].value.messages
            if messages and len(messages) > 0:
                return messages[0]
        except (IndexError, AttributeError):
            pass
        return None
    
    def _extract_phone_number_id(self, payload: WhatsAppWebhookPayload) -> str:
        """Estrae il phone number ID dal payload."""
        return payload.entry[0].changes[0].value.metadata.phone_number_id
    
    def _extract_message_text(self, message: WhatsAppMessage) -> str:
        """Estrae il testo dal messaggio."""
        if message.type == "text" and message.text:
            return message.text.body
        
        if message.type == "interactive" and message.interactive:
            if message.interactive.button_reply:
                return message.interactive.button_reply.title
            if message.interactive.list_reply:
                return message.interactive.list_reply.title
        
        if message.type == "button" and message.button:
            return message.button.text
        
        return ""
    
    def _extract_button_payload(self, message: WhatsAppMessage) -> Optional[str]:
        """Estrae il payload del bottone se presente."""
        if message.type == "interactive" and message.interactive:
            if message.interactive.button_reply:
                return message.interactive.button_reply.id
            if message.interactive.list_reply:
                return message.interactive.list_reply.id
        
        if message.type == "button" and message.button:
            return message.button.payload
        
        return None