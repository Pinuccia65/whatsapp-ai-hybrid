"""
WhatsApp Schemas.

Definisce gli schemi Pydantic per i payload webhook
di WhatsApp Business API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class WhatsAppMetadata(BaseModel):
    """Metadata del messaggio."""
    display_phone_number: str
    phone_number_id: str


class WhatsAppProfile(BaseModel):
    """Profilo contatto."""
    name: str


class WhatsAppContact(BaseModel):
    """Contatto WhatsApp."""
    wa_id: str
    profile: WhatsAppProfile


class WhatsAppText(BaseModel):
    """Messaggio testo."""
    body: str


class WhatsAppButtonReply(BaseModel):
    """Risposta bottone."""
    id: str
    title: str


class WhatsAppListReply(BaseModel):
    """Risposta lista."""
    id: str
    title: str
    description: Optional[str] = None


class WhatsAppInteractive(BaseModel):
    """Messaggio interattivo."""
    type: str  # 'button_reply' | 'list_reply'
    button_reply: Optional[WhatsAppButtonReply] = None
    list_reply: Optional[WhatsAppListReply] = None


class WhatsAppButton(BaseModel):
    """Bottone legacy."""
    text: str
    payload: str


class WhatsAppMessage(BaseModel):
    """Messaggio WhatsApp."""
    from_: str = Field(alias="from")
    id: str
    timestamp: str
    type: str  # 'text' | 'interactive' | 'button'
    text: Optional[WhatsAppText] = None
    interactive: Optional[WhatsAppInteractive] = None
    button: Optional[WhatsAppButton] = None
    
    class Config:
        populate_by_name = True


class WhatsAppStatus(BaseModel):
    """Stato messaggio."""
    id: str
    status: str  # 'sent' | 'delivered' | 'read' | 'failed'
    timestamp: str
    recipient_id: str


class WhatsAppValue(BaseModel):
    """Valore del webhook."""
    messaging_product: str
    metadata: WhatsAppMetadata
    contacts: Optional[List[WhatsAppContact]] = None
    messages: Optional[List[WhatsAppMessage]] = None
    statuses: Optional[List[WhatsAppStatus]] = None


class WhatsAppChange(BaseModel):
    """Change del webhook."""
    value: WhatsAppValue
    field: str


class WhatsAppEntry(BaseModel):
    """Entry del webhook."""
    id: str
    changes: List[WhatsAppChange]


class WhatsAppWebhookPayload(BaseModel):
    """Payload completo webhook WhatsApp."""
    object: str
    entry: List[WhatsAppEntry]