FROM python:3.10-slim

WORKDIR /app

# Copiar los requerimientos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script de Python
COPY main.py .

# Exponer el puerto del FastAPI
EXPOSE 8000

# Comando para arrancar el servidor
CMD ["python", "main.py"]
