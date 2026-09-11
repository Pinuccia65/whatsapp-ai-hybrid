# WhatsApp AI Receptionist

Sistema di ricezione automatica per prenotazioni via WhatsApp con AI.
Sviluppato in Python con FastAPI, deployabile su Render.

## Stack Tecnologico

- **FastAPI** - Framework web asincrono
- **Supabase** - Database PostgreSQL + API REST (sostituisce MongoDB + Redis)
- **OpenAI** - Intent extraction
- **WhatsApp Business Cloud API** - Integrazione messaging
- **Render** - Hosting

## Struttura

```
app/
├── main.py              # Entry point FastAPI
├── config.py            # Configurazione environment
├── api/routes/          # Endpoint HTTP
├── services/            # Logica di business
├── schemas/             # Pydantic schemas
└── utils/               # Utility
supabase/
└── schema.sql           # Schema SQL per Supabase
```

## Setup

1. Crea progetto su supabase.com
2. Esegui supabase/schema.sql nel SQL Editor
3. Copia URL e key nelle variabili ambiente
4. pip install -r requirements.txt
5. uvicorn app.main:app --reload

## Variabili ambiente

- SUPABASE_URL - URL del progetto Supabase
- SUPABASE_KEY - Chiave anon o service_role
- OPENAI_API_KEY - Chiave OpenAI
- WHATSAPP_TOKEN - Token WhatsApp Business
- WHATSAPP_VERIFY_TOKEN - Token verifica webhook
