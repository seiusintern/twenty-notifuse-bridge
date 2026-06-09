from fastapi import FastAPI, Request, BackgroundTasks
from prefect import flow, task
from prefect.client.orchestration import get_client
import uvicorn
import requests

app = FastAPI()
NOTIFUSE_API_URL = "http://notifuse.seius.com.ec/api/v1/transactional" # Tu URL interna en Dokploy

@task(retries=3, retry_delay_seconds=10)
def enviar_a_notifuse(payload: dict):
    # Esto ejecuta el envío real hacia Notifuse
    response = requests.post(NOTIFUSE_API_URL, json=payload)
    if response.status_code not in [200, 201]:
        raise Exception(f"Error en Notifuse: {response.status_code}")

@flow(name="Sincronizar Cliente Twenty - Notifuse")
def crm_sync_flow(twenty_data: dict):
    # 1. Extraer los datos del JSON de Twenty
    emails = twenty_data.get("emails", [])
    email_principal = emails[0].get("email") if emails else None
    
    if not email_principal:
        return {"status": "ignored", "reason": "No email found"}

    # 2. Mapear al formato plano de Notifuse
    notifuse_payload = {
        "email": email_principal,
        "first_name": twenty_data.get("name", {}).get("firstName", ""),
        "last_name": twenty_data.get("name", {}).get("lastName", ""),
        "external_id": twenty_data.get("id")
    }

    # 3. Enviar
    enviar_a_notifuse(notifuse_payload)

# Este es el endpoint que va a escuchar a Twenty CRM
@app.post("/webhook")
async def receive_twenty_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    twenty_data = payload.get("data", {})
    
    # Lanzamos el flujo de Prefect en segundo plano para no bloquear a Twenty
    background_tasks.add_task(crm_sync_flow, twenty_data)
    
    return {"status": "accepted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
