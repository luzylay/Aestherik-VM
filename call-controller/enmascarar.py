import re

texto = ("Buenos dias, gracias por llamar a ventas. "
         "Si claro, mi numero de tarjeta es 4532 1234 5678 9010 "
         "y mi telefono es 987654321. Muchas gracias por su ayuda.")

print("===== TEXTO ORIGINAL =====")
print(texto)

patron_tarjeta = r"\b(?:\d[ -]?){13,16}\b"
texto_limpio = re.sub(patron_tarjeta, "[TARJETA OCULTA ****] ", texto)

print("\n===== TEXTO ENMASCARADO (seguro para guardar) =====")
print(texto_limpio)

palabras_cortesia = ["buenos dias", "buenas tardes", "gracias", "por favor", "con gusto"]
encontradas = []
for palabra in palabras_cortesia:
    if palabra in texto.lower():
        encontradas.append(palabra)
puntaje = len(encontradas) * 25
if puntaje > 100:
    puntaje = 100

print("\n===== ANALISIS DE CALIDAD =====")
print(f"Palabras de cortesia detectadas: {encontradas}")
print(f"Puntaje de calidad: {puntaje} de 100")
