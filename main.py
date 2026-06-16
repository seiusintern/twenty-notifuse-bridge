import os
import requests
import urllib3
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

# Desactivar los warnings de TLS/SSL por usar la IP interna
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(title="Puente Twenty CRM a Notifuse")

# Configuración fija del backend Notifuse (Red interna del VPS)
NOTIFUSE_URL = "https://172.17.0.1:443/api/contacts.upsert"
NOTIFUSE_HEADERS = {
    "Host": "notifuse.seius.com.ec",
    "Content-Type": "application/json"
}
WORKSPACE_ID = "seius"

# --- Modelos de datos para mapear el JSON dinámico de Twenty CRM ---
class TwentyEmail(BaseModel):
    email: str
    primary: Optional[bool] = True

class TwentyPersonData(BaseModel):
    firstName: Optional[str] = ""
    lastName: Optional[str] = ""
    emails: List[TwentyEmail]

class TwentyWebhookPayload(BaseModel):
    action: str  # Ejemplo: "person.created" o "person.updated"
    data: TwentyPersonData

# --- Endpoint que escuchará a Twenty CRM ---
@app.post("/webhook/twenty-to-notifuse")
async def handle_twenty_webhook(payload: TwentyWebhookPayload):
    """
    Recibe el evento dinámico de Twenty CRM, extrae los datos del contacto
    y los envía estructurados a Notifuse de forma automática.
    """
    person = payload.data
    
    # 1. Extraer el email principal del arreglo de correos de Twenty
    if not person.emails:
        raise HTTPException(status_code=400, detail="El contacto de Twenty no tiene correos asignados.")
    
    # Buscamos el primario, si no hay, agarramos el primero de la lista
    primary_email_obj = next((e for e in person.emails if e.primary), person.emails[0])
    email_dinamico = primary_email_obj.email

    # 2. Mapear al formato estricto que requiere Notifuse
    notifuse_payload = {
        "workspace_id": WORKSPACE_ID,
        "contact": {
            "email": email_dinamico,
            "first_name": person.firstName,
            "last_name": person.lastName
        }
    }

    # 3. Despachar los datos dinámicos al contenedor local de Notifuse
    try:
        print(f"Procesando Webhook [{payload.action}] para: {email_dinamico}")
        response = requests.post(
            NOTIFUSE_URL, 
            json=notifuse_payload, 
            headers=NOTIFUSE_HEADERS, 
            verify=False, 
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            return {
                "status": "success", 
                "message": f"Contacto {email_dinamico} sincronizado dinámicamente en Notifuse.",
                "backend_response": response.json()
            }
        else:
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Notifuse rechazó los datos: {response.text}"
            )
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error en la red interna hacia Notifuse: {str(e)}"
        )

# Para correrlo localmente si deseas probar: uvicorn main:app --host 0.0.0.0 --port 8000
