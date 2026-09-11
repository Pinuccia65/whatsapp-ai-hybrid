"""WhatsApp Schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


class WhatsAppMetadata(BaseModel):
    display_phone_number: str
    phone_number_id: str


class WhatsAppText(BaseModel):
    body: str


class WhatsAppButtonReply(BaseModel):
    id: str
    title: str


class WhatsAppListReply(BaseModel):
    id: str
    title: str


class WhatsAppInteractive(BaseModel):
    type: str
    button_reply: Optional[WhatsAppButtonReply] = None
    list_reply: Optional[WhatsAppListReply] = None


class WhatsAppButton(BaseModel):
    text: str
    payload: str


class WhatsAppMessage(BaseModel):
    from_: str = Field(alias="from")
    id: str
    timestamp: str
    type: str
    text: Optional[WhatsAppText] = None
    interactive: Optional[WhatsAppInteractive] = None
    button: Optional[WhatsAppButton] = None
    
    class Config:
        populate_by_name = True


class WhatsAppValue(BaseModel):
    messaging_product: str
    metadata: WhatsAppMetadata
    messages: Optional[List[WhatsAppMessage]] = None


class WhatsAppChange(BaseModel):
    value: WhatsAppValue
    field: str


class WhatsAppEntry(BaseModel):
    id: str
    changes: List[WhatsAppChange]


class WhatsAppWebhookPayload(BaseModel):
    object: str
    entry: List[WhatsAppEntry]