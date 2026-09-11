# WhatsApp AI Receptionist

Sistema di ricezione automatica per prenotazioni via WhatsApp con AI, sviluppato in Python e deployabile su Render.

## Stack Tecnologico

- **FastAPI** - Framework web asincrono
- **MongoDB + Motor** - Database documentale (async)
- **Redis** - Gestione sessioni conversazione
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
├── models/              # Modelli MongoDB
├── schemas/             # Pydantic schemas
└── utils/               # Utility
```

## Setup Locale

```bash
# Crea virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Installa dipendenze
pip install -r requirements.txt

# Configura variabili ambiente
cp .env.example .env
# Modifica .env con le tue credenziali

# Avvia server
uvicorn app.main:app --reload
```

## Deploy su Render

1. Push del codice su GitHub
2. Crea nuovo "Web Service" su Render
3. Collega il repository
4. Configura environment variables
5. Deploy automatico

## Variabili ambiente

- `MONGODB_URI` - Connessione MongoDB
- `REDIS_URL` - Connessione Redis
- `OPENAI_API_KEY` - Chiave OpenAI
- `WHATSAPP_TOKEN` - Token WhatsApp Business
- `WHATSAPP_VERIFY_TOKEN` - Token verifica webhook
- `WHATSAPP_API_URL` - URL API WhatsApp (default: graph.facebook.com)

## Flusso

1. Utente invia messaggio WhatsApp
2. Webhook riceve → FastAPI endpoint
3. AI Intent Service estrae parametri
4. Booking State determina prossimo passo
5. Availability Engine calcola slot reali
6. Message Builder crea messaggio con bottoni
7. WhatsApp invia risposta all'utente
