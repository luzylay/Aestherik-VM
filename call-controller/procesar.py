import glob
import os
import re
import datetime
from faster_whisper import WhisperModel
from pymongo import MongoClient

archivos = glob.glob("../recordings/*.wav")
if not archivos:
    archivos = glob.glob("*.wav")
if not archivos:
    print("No encontre ninguna grabacion .wav")
    raise SystemExit

archivo = max(archivos, key=os.path.getmtime)
print(f"Procesando grabacion: {archivo}")

print("Transcribiendo con Whisper (small)...")
modelo = WhisperModel("small", device="cpu", compute_type="int8")
segmentos, info = modelo.transcribe(archivo, language="es")
texto = ""
for s in segmentos:
    texto = texto + s.text
print(f"Texto reconocido: {texto}")

patron_tarjeta = r"\b(?:\d[ -]?){13,16}\b"
texto_seguro = re.sub(patron_tarjeta, "[TARJETA OCULTA ****] ", texto)

palabras_cortesia = ["buenos dias", "buenas tardes", "gracias", "por favor", "con gusto"]
encontradas = []
for palabra in palabras_cortesia:
    if palabra in texto.lower():
        encontradas.append(palabra)
puntaje = len(encontradas) * 25
if puntaje > 100:
    puntaje = 100

uri = "mongodb://admin:admin123@localhost:27017/marcacion_db?authSource=admin"
cliente = MongoClient(uri)
db = cliente["marcacion_db"]
documento = {
    "agent_extension": "6001",
    "caller_number": "8000",
    "status": "procesada",
    "duration_seconds": 0,
    "recording_path": os.path.basename(archivo),
    "texto_seguro": texto_seguro,
    "puntaje": puntaje,
    "created_at": datetime.datetime.now(),
}
db.calls.insert_one(documento)
db.transcriptions.insert_one(documento)
print("\nGuardado en MongoDB correctamente.")
