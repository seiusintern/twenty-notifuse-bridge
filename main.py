import os
import requests
import urllib3

# Desactivar los warnings molestos de TLS/SSL por usar la IP interna con -k
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def upsert_notifuse_contact(email, first_name="", last_name=""):
    """
    Registra o actualiza un contacto en Notifuse saltándose Cloudflare
    usando la red local del VPS.
    """
    # 1. Configuración de la URL interna y el Host virtual para Traefik
    url = "https://127.0.0.1:443/api/contacts.upsert"
    
    headers = {
        "Host": "notifuse.seius.com.ec",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTY1ODUwYTMtMzIxMC00NDM0LWIxMDgtNjU5MTUxMWRjZmNmIiwidHlwZSI6ImFwaV9rZXkiLCJlbWFpbCI6ImNybUBub3RpZnVzZS5zZWl1cy5jb20uZWMiLCJleHAiOjIwOTYzOTg4MjUsIm5iZiI6MTc4MTAzODgyNSwiaWF0IjoxNzgxMDM4ODI1fQ.KXCMxplkGTCZedrles6ZTM71yg3AdwW5y8l7NYKl8_4",
        "Content-Type": "application/json"
    }

    # 2. Tu estructura de JSON perfecta (validada con 'seius' en minúsculas)
    payload = {
        "workspace_id": "seius",
        "contact": {
            "email": email,
            "first_name": first_name,
            "last_name": last_name
        }
    }

    try:
        # 3. Realizar la petición HTTP POST (verify=False equivale al -k de curl)
        print(f"Enviando contacto a Notifuse: {email}...")
        response = requests.post(url, json=payload, headers=headers, verify=False, timeout=10)
        
        # 4. Manejo y lectura de la respuesta
        if response.status_code in [200, 201]:
            print("¡Éxito! Contacto guardado correctamente en Notifuse.")
            print("Respuesta del servidor:", response.json())
            return True
        else:
            print(f"Error al guardar contacto. Código de estado: {response.status_code}")
            print("Detalle del backend:", response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Error crítico de conexión con el contenedor de Notifuse: {e}")
        return False

# ==========================================
# Ejemplo de uso (Prueba de ejecución rápida)
# ==========================================
if __name__ == "__main__":
    # Datos de prueba para verificar que el puente funcione desde Python
    test_email = "alexander.upsert.python@seius.com.ec"
    test_name = "Alexander"
    test_lastname = "Paillacho"
    
    upsert_notifuse_contact(test_email, test_name, test_lastname)
