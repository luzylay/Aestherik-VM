import glob
import os
from faster_whisper import WhisperModel

archivos = glob.glob("*.wav")
if not archivos:
    print("No encontre ningun archivo .wav en esta carpeta.")
    raise SystemExit

archivo = max(archivos, key=os.path.getmtime)
print(f"Voy a transcribir: {archivo}")

modelo = WhisperModel("small", device="cpu", compute_type="int8")
segmentos, info = modelo.transcribe(archivo, language="es")

print("\n========== TEXTO DE LA LLAMADA ==========")
texto = ""
for s in segmentos:
    print(s.text)
    texto = texto + s.text
print("=========================================\n")

salida = archivo + ".txt"
with open(salida, "w") as f:
    f.write(texto)
print(f"Listo. Texto guardado en: {salida}")
