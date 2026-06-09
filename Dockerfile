FROM python:3.10-slim

WORKDIR /app

# Copiar e instalar las dependencias desde el requirements corregido
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de tu aplicación (incluyendo tu main.py)
COPY . .

# Exponer el puerto 8000 que es donde FastAPI escuchará los webhooks
EXPOSE 8000

# Comando para arrancar Uvicorn y mantener el servicio vivo
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
