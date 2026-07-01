# Control de Llamadas ARI con Bridge (Versión de Producción)
# Conecta cliente (8000) con agente (6001), graba la conversación
# y encola la grabación en Redis para procesamiento asíncrono.
import json
import time
import requests
import websocket
import redis
import config

# Credenciales y rutas de ARI
ARI_URL = f"http://{config.ARI_HOST}:{config.ARI_PORT}/ari"
AUTH = (config.ARI_USER, config.ARI_PASS)

# Cliente Redis para encolar tareas
try:
    redis_client = redis.Redis(
        host=config.REDIS_HOST, 
        port=config.REDIS_PORT, 
        decode_responses=True
    )
    print(f"[REDIS] Conectado a {config.REDIS_HOST}:{config.REDIS_PORT}")
except Exception as e:
    print(f"[ADVERTENCIA] No se pudo establecer conexión inicial con Redis: {e}")
    redis_client = None

# Seguimiento de llamadas activas
# channel_id -> { start_time, caller_number, recording_name, bridge_id }
llamadas_activas = {}
bridge_id = None

def contestar(channel_id):
    requests.post(f"{ARI_URL}/channels/{channel_id}/answer", auth=AUTH)
    print(f"  -> Cliente {channel_id} CONTESTADO")

def crear_bridge():
    r = requests.post(f"{ARI_URL}/bridges", auth=AUTH, params={"type": "mixing"})
    bid = r.json()["id"]
    print(f"  -> Bridge creado: {bid}")
    return bid

def unir_al_bridge(bid, channel_id):
    requests.post(f"{ARI_URL}/bridges/{bid}/addChannel", auth=AUTH,
                  params={"channel": channel_id})
    print(f"  -> Canal {channel_id} unido al bridge {bid}")

def grabar_bridge(bid):
    nombre = f"llamada_doble_{int(time.time())}"
    requests.post(f"{ARI_URL}/bridges/{bid}/record", auth=AUTH,
                  params={"name": nombre, "format": "wav",
                          "ifExists": "overwrite", "terminateOn": "none"})
    print(f"  -> GRABANDO bridge en: {nombre}.wav")
    return nombre

def llamar_agente():
    # Usamos appArgs="agente" para identificar el canal cuando StasisStart se active
    requests.post(f"{ARI_URL}/channels", auth=AUTH,
                  params={
                      "endpoint": config.AGENTE, 
                      "app": config.APP_NAME,
                      "appArgs": "agente",
                      "callerId": "CallCenter <8000>"
                  })
    print(f"  -> Llamando al agente {config.AGENTE}...")

def encolar_llamada(nombre_grabacion, duracion, caller_number):
    if not redis_client:
        print("[ERROR] Redis no está disponible. Saltando encolamiento.")
        return
    try:
        payload = {
            "recording_path": f"{nombre_grabacion}.wav",
            "agent_extension": config.AGENTE.split("/")[-1],
            "caller_number": caller_number,
            "duration_seconds": duracion
        }
        redis_client.rpush("callcenter_queue", json.dumps(payload))
        print(f"  -> [REDIS] Grabación encolada para procesar: {nombre_grabacion}.wav ({duracion}s)")
    except Exception as e:
        print(f"[ERROR] No se pudo encolar en Redis: {e}")

def al_recibir_evento(ws, mensaje):
    global bridge_id
    evento = json.loads(mensaje)
    tipo = evento.get("type")
    
    if tipo == "StasisStart":
        canal = evento["channel"]
        channel_id = canal["id"]
        args = evento.get("args", [])
        
        if "agente" in args:
            print(f"\n[AGENTE] Contestó el agente: {channel_id}")
            if bridge_id:
                unir_al_bridge(bridge_id, channel_id)
        else:
            print(f"\n[CLIENTE] Entró llamada al 8000: {channel_id}")
            contestar(channel_id)
            bridge_id = crear_bridge()
            unir_al_bridge(bridge_id, channel_id)
            nombre_grabacion = grabar_bridge(bridge_id)
            
            # Registrar metadatos e inicio de llamada
            llamadas_activas[channel_id] = {
                "start_time": time.time(),
                "caller_number": canal.get("caller", {}).get("number", "desconocido"),
                "recording_name": nombre_grabacion,
                "bridge_id": bridge_id
            }
            llamar_agente()
            
    elif tipo == "StasisEnd":
        channel_id = evento["channel"]["id"]
        print(f"[FIN] Canal {channel_id} salió.")
        if channel_id in llamadas_activas:
            # La llamada del cliente terminó, calculamos duración y encolamos
            datos = llamadas_activas.pop(channel_id)
            duracion = int(time.time() - datos["start_time"])
            encolar_llamada(datos["recording_name"], duracion, datos["caller_number"])

def al_abrir(ws):
    print("=" * 65)
    print(f" Conectado a Asterisk ARI ({config.ARI_HOST}:{config.ARI_PORT})")
    print(f" Aplicación Stasis: {config.APP_NAME}. Esperando llamadas al 8000...")
    print("=" * 65)

def al_error(ws, error):
    print(f"[ERROR] WebSocket: {error}")

def al_cerrar(ws, codigo, mensaje):
    print("[DESCONECTADO] Conexión de eventos ARI cerrada.")

# Bucle principal de WebSocket para eventos ARI
ws_url = (f"ws://{config.ARI_HOST}:{config.ARI_PORT}/ari/events"
          f"?app={config.APP_NAME}&api_key={config.ARI_USER}:{config.ARI_PASS}")

ws = websocket.WebSocketApp(ws_url, 
                            on_open=al_abrir, 
                            on_message=al_recibir_evento,
                            on_error=al_error, 
                            on_close=al_cerrar)

if __name__ == "__main__":
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo controlador de llamadas.")
