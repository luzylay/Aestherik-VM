# Background Worker - Procesamiento Asíncrono de Llamadas (Whisper + Mongo)
# Escucha la cola de Redis y procesa grabaciones de audio automáticamente.
import os
import re
import json
import time
import datetime
from faster_whisper import WhisperModel
from pymongo import MongoClient
import redis
import config

print("=" * 65)
print(" Iniciando Worker de Procesamiento Inteligente de Llamadas")
print(f" Carga de modelo Whisper 'small' en CPU (int8)...")
print("=" * 65)

# Cargar modelo Whisper al arrancar (una sola vez)
try:
    # download_root puede configurarse si deseamos guardar los pesos en un volumen
    model = WhisperModel("small", device="cpu", compute_type="int8")
    print("[LOG] Modelo Whisper cargado con éxito.")
except Exception as e:
    print(f"[CRÍTICO] Error al cargar el modelo Whisper: {e}")
    raise SystemExit(1)

# Conectar a MongoDB
try:
    mongo_client = MongoClient(config.MONGO_URI)
    db = mongo_client.get_default_database() # obtiene la DB definida en la URI (marcacion_db)
    # Crear índices para acelerar búsquedas en dashboard
    db.calls.create_index([("created_at", -1)])
    print(f"[LOG] Conectado a MongoDB: {config.MONGO_URI.split('@')[-1]}")
except Exception as e:
    print(f"[CRÍTICO] Error al conectar a MongoDB: {e}")
    raise SystemExit(1)

# Conectar a Redis
try:
    redis_client = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        decode_responses=True
    )
    print(f"[LOG] Conectado a Redis en {config.REDIS_HOST}:{config.REDIS_PORT}")
except Exception as e:
    print(f"[CRÍTICO] Error de conexión a Redis: {e}")
    raise SystemExit(1)

# Reglas de Calidad y Seguridad
PATRON_TARJETA = r"\b(?:\d[ -]?){13,16}\b"
PALABRAS_CORTESIA = ["buenos dias", "buenas tardes", "buenas noches", "gracias", "por favor", "con gusto", "un placer"]

def enmascarar_texto(texto):
    if not texto:
        return ""
    return re.sub(PATRON_TARJETA, "[TARJETA OCULTA ****] ", texto)

def calcular_calidad(texto):
    if not texto:
        return 0
    encontradas = []
    texto_min = texto.lower()
    for palabra in PALABRAS_CORTESIA:
        if palabra in texto_min:
            encontradas.append(palabra)
    
    # Cada frase de cortesía otorga 25 puntos (máximo 100)
    puntaje = len(encontradas) * 25
    return min(puntaje, 100)

def procesar_audio(payload):
    recording_path = payload.get("recording_path")
    agent_extension = payload.get("agent_extension", "desconocido")
    caller_number = payload.get("caller_number", "desconocido")
    duration_seconds = payload.get("duration_seconds", 0)

    # Determinar ruta completa del archivo de audio
    ruta_audio = os.path.join(config.RECORDINGS_DIR, recording_path)
    print(f"\n[PROCESO] Iniciando procesamiento para: {recording_path}")
    print(f"  Ruta física esperada: {ruta_audio}")

    # Esperar hasta que el archivo esté listo y tenga tamaño completo
    intentos = 0
    while not os.path.exists(ruta_audio) or os.path.getsize(ruta_audio) == 0:
        if intentos >= 10:
            print(f"  [ERROR] El archivo de audio no apareció después de 10 segundos. Abortando.")
            return False
        print(f"  [INFO] Esperando a que se guarde el archivo en disco (intento {intentos + 1}/10)...")
        time.sleep(1)
        intentos += 1

    time.sleep(0.5) # Pausa final de seguridad para evitar locks de lectura/escritura

    # Transcripción STT
    print("  Transcribiendo audio con Whisper...")
    start_time = time.time()
    try:
        segments, info = model.transcribe(ruta_audio, language="es")
        texto_completo = " ".join([segment.text for segment in segments]).strip()
        transcription_time = round(time.time() - start_time, 2)
        print(f"  Transcripción completada en {transcription_time}s.")
        print(f"  Texto crudo: '{texto_completo}'")
    except Exception as e:
        print(f"  [ERROR] Falla durante la transcripción: {e}")
        texto_completo = "[ERROR EN TRANSCRIPCIÓN]"

    # Seguridad y Calidad
    texto_seguro = enmascarar_texto(texto_completo)
    contiene_tarjeta = texto_seguro != texto_completo
    puntaje = calcular_calidad(texto_completo)

    # Guardar en MongoDB
    documento = {
        "agent_extension": agent_extension,
        "caller_number": caller_number,
        "status": "procesada",
        "duration_seconds": duration_seconds,
        "recording_path": recording_path,
        "texto_seguro": texto_seguro,
        "contiene_tarjeta": contiene_tarjeta,
        "puntaje": puntaje,
        "created_at": datetime.datetime.now(),
    }

    try:
        # Se inserta en 'calls' y en 'transcriptions' para mantener compatibilidad
        db.calls.insert_one(documento)
        print(f"  [ÉXITO] Documento guardado en base de datos. Calidad: {puntaje}/100. Enmascarado: {contiene_tarjeta}.")
        return True
    except Exception as e:
        print(f"  [ERROR] No se pudo guardar en MongoDB: {e}")
        return False

def main():
    print("\n[WORKER] Escuchando la cola 'callcenter_queue'...")
    while True:
        try:
            # blpop bloquea la conexión hasta que llegue un elemento
            resultado = redis_client.blpop("callcenter_queue", timeout=0)
            if resultado:
                # blpop devuelve una tupla (nombre_cola, valor)
                _, datos_str = resultado
                try:
                    payload = json.loads(datos_str)
                    procesar_audio(payload)
                except json.JSONDecodeError:
                    print(f"[ERROR] Mensaje mal formateado en la cola: {datos_str}")
        except KeyboardInterrupt:
            print("\nWorker detenido por el usuario.")
            break
        except Exception as e:
            print(f"[ADVERTENCIA] Error inesperado en el loop principal: {e}")
            time.sleep(5) # Evitar loops infinitos rápidos si hay desconexiones graves

if __name__ == "__main__":
    main()
