import json
import time
import requests
import websocket

ARI_USER = "ariuser"
ARI_PASS = "aripass"
ARI_HOST = "localhost"
ARI_PORT = 8088
APP_NAME = "callcenter-app"

ARI_URL = f"http://{ARI_HOST}:{ARI_PORT}/ari"
AUTH = (ARI_USER, ARI_PASS)

def contestar(channel_id):
    requests.post(f"{ARI_URL}/channels/{channel_id}/answer", auth=AUTH)
    print(f"  -> Llamada {channel_id} CONTESTADA")

def reproducir_saludo(channel_id):
    requests.post(f"{ARI_URL}/channels/{channel_id}/play", auth=AUTH,
                  params={"media": "sound:hello-world"})
    print(f"  -> Reproduciendo saludo en {channel_id}")

def grabar(channel_id):
    nombre = f"llamada_{int(time.time())}"
    requests.post(f"{ARI_URL}/channels/{channel_id}/record", auth=AUTH,
                  params={"name": nombre, "format": "wav", "maxDurationSeconds": 30,
                          "beep": "true", "terminateOn": "#", "ifExists": "overwrite"})
    print(f"  -> GRABANDO en archivo: {nombre}.wav")

def colgar(channel_id):
    requests.delete(f"{ARI_URL}/channels/{channel_id}", auth=AUTH)

def al_recibir_evento(ws, mensaje):
    evento = json.loads(mensaje)
    tipo = evento.get("type")
    if tipo == "StasisStart":
        channel_id = evento["channel"]["id"]
        print(f"\n[LLAMADA NUEVA] Entro una llamada: {channel_id}")
        contestar(channel_id)
        reproducir_saludo(channel_id)
    elif tipo == "PlaybackFinished":
        channel_id = evento["playback"]["target_uri"].replace("channel:", "")
        grabar(channel_id)
    elif tipo == "RecordingFinished":
        nombre = evento["recording"]["name"]
        print(f"  -> Grabacion terminada y guardada: {nombre}.wav")
    elif tipo == "StasisEnd":
        channel_id = evento["channel"]["id"]
        print(f"[FIN] La llamada {channel_id} termino\n")

def al_abrir(ws):
    print("=" * 55)
    print(" Conectado a Asterisk por ARI. Esperando llamadas...")
    print(" Marca la extension 8000 desde el Zoiper para probar.")
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
