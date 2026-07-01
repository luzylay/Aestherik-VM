# Acerca de Aestherik-VM

Este documento proporciona una visión detallada, el contexto y la justificación del diseño del proyecto **Aestherik-VM** (Asistente de Marcación Inteligente y Análisis de Calidad).

---

## 🎯 Motivación y Contexto

En el sector de los Centros de Contacto (Call Centers), la evaluación de calidad de las llamadas tradicionalmente ha dependido de auditores humanos que escuchan grabaciones aleatorias. Este enfoque presenta dos desafíos críticos:

1. **Eficiencia y Cobertura**: Un supervisor humano solo puede auditar un pequeño porcentaje (típicamente del 1% al 5%) del total de llamadas debido al tiempo que esto consume.
2. **Riesgos de Privacidad (PCI-DSS)**: Durante el transcurso de una llamada (por ejemplo, al procesar pagos), los clientes dictan números de tarjetas de crédito o datos personales. Si estos se graban y almacenan sin cifrar, la empresa incumple la normativa de seguridad de datos de la industria de tarjetas de pago (PCI-DSS), exponiéndose a sanciones graves.

**Aestherik-VM** nace como un prototipo de laboratorio de nivel profesional para automatizar el control de calidad mediante Inteligencia Artificial (Whisper) de forma local (asegurando privacidad absoluta del canal de voz) y aplicar enmascarado inmediato de datos sensibles antes de persistirlos.

---

## ⚙️ ¿Cómo Funciona la Solución?

El ciclo de vida de una interacción telefónica en el sistema sigue tres fases clave:

### Fase 1: Captura e Interceptación (Telefonía / Asterisk / ARI)
Cuando el cliente llama a la línea de atención (`8000`), Asterisk no utiliza el plan de marcado convencional (`dialplan`) para conectar la llamada de forma pasiva. En su lugar, transfiere el control de la llamada a la aplicación externa en Python a través de **Stasis** (por WebSocket). 
El script de Python contesta, crea una sala de mezcla virtual (bridge), conecta al agente y al cliente, e instruye a Asterisk a iniciar la grabación. Esto permite controlar la llamada de manera asíncrona (ejemplo: detectar colgues de canal de forma inmediata).

### Fase 2: Cola Desacoplada (Redis)
Al finalizar la llamada, el audio grabado se guarda en el disco compartido. Para evitar retrasar la infraestructura telefónica o la base de datos web mientras se realiza la transcripción de IA (la cual consume mucha CPU/GPU), los metadatos de la llamada se envían a una cola de mensajes en **Redis**. Esto asegura que si ingresan múltiples llamadas de forma simultánea, Asterisk continúe respondiendo sin demoras.

### Fase 3: Procesamiento Cognitivo (Worker de Whisper + Reglas)
El **Worker** procesa las tareas una a una. 
- Extrae la transcripción del audio a través de **Whisper Model**, que funciona de forma local (offline).
- Analiza el texto para detectar patrones numéricos de 13 a 16 dígitos correspondientes a tarjetas bancarias (Visa, Mastercard, etc.) y los reemplaza por una etiqueta de seguridad.
- Escanea el texto en busca de fórmulas verbales de cortesía ("buenos días", "gracias", "por favor") para calificar la llamada.
- Guarda la información procesada en **MongoDB**.

---

## 📊 Beneficios de la Arquitectura

- **Seguridad Activa (Privacy by Design)**: Al procesar la transcripción y el enmascarado de forma local mediante Whisper, ningún audio o dato sensible es enviado a APIs de terceros en la nube (como OpenAI o Google Cloud STT).
- **Escalabilidad**: Al separar el controlador telefónico, el worker de IA y el dashboard mediante Docker, cada servicio puede escalarse de manera independiente según la demanda.
- **Resiliencia**: Si la base de datos MongoDB se desconecta temporalmente, la cola de Redis mantiene las tareas a salvo para procesarlas una vez restaurado el servicio.

---
*Aestherik-VM es un proyecto de laboratorio desarrollado por el Grupo 05.*
