FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia codice
COPY . .

# Esponi porta
EXPOSE 8000

# Avvia applicazione
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]