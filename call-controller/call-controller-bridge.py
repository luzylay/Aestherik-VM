# NOTA: version RECONSTRUIDA del flujo con bridge (mejora).
# Reemplazar por tu archivo real si difiere. Comportamiento:
# cliente marca 8000 -> se crea un mixing bridge -> se une al cliente ->
# se graba el bridge -> se origina llamada al agente 6001 -> se une al bridge.
import json
import time
import requests
import websocket

ARI_USER = "ariuser"
ARI_PASS = "aripass"
ARI_HOST = "localhost"
ARI_PORT = 8088
APP_NAME = "callcenter-app"
AGENTE = "PJSIP/6001"

ARI_URL = f"http://{ARI_HOST}:{ARI_PORT}/ari"
AUTH = (ARI_USER, ARI_PASS)

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

def llamar_agente():
    requests.post(f"{ARI_URL}/channels", auth=AUTH,
                  params={"endpoint": AGENTE, "app": APP_NAME,
                          "callerId": "CallCenter <8000>"})
    print(f"  -> Llamando al agente {AGENTE}...")

def al_recibir_evento(ws, mensaje):
    global bridge_id
    evento = json.loads(mensaje)
    tipo = evento.get("type")
    if tipo == "StasisStart":
        canal = evento["channel"]
        channel_id = canal["id"]
        args = evento.get("args", [])
        if "agente" in args:
            print(f"\n[AGENTE] Contesto el agente: {channel_id}")
            unir_al_bridge(bridge_id, channel_id)
        else:
            print(f"\n[CLIENTE] Entro una llamada al 8000: {channel_id}")
            contestar(channel_id)
            bridge_id = crear_bridge()
            unir_al_bridge(bridge_id, channel_id)
            grabar_bridge(bridge_id)
            llamar_agente()
    elif tipo == "StasisEnd":
        print(f"[FIN] Canal {evento['channel']['id']} salio\n")

def al_abrir(ws):
    print("=" * 55)
    print(" Conectado a Asterisk por ARI (modo bridge). Esperando 8000...")
    print("=" * 55)

def al_error(ws, error):
    print(f"[ERROR] {error}")

def al_cerrar(ws, codigo, mensaje):
    print("[DESCONECTADO] Se cerro la conexion con Asterisk.")

ws_url = (f"ws://{ARI_HOST}:{ARI_PORT}/ari/events"
          f"?app={APP_NAME}&api_key={ARI_USER}:{ARI_PASS}")
ws = websocket.WebSocketApp(ws_url, on_open=al_abrir, on_message=al_recibir_evento,
                            on_error=al_error, on_close=al_cerrar)
ws.run_forever()
