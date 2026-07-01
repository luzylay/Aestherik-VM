# Call Center Inteligente con Asterisk

**Proyecto 3 — Asistente de Marcación Inteligente y Análisis de Calidad**
Plataforma que conecta telefonía VoIP con análisis por Inteligencia Artificial: contesta llamadas, las graba, las transcribe con Whisper, oculta datos sensibles y lo muestra todo en un dashboard web.

> **Grupo 05** · Lady Loayza · Jose Castro · Andy Vergara

---

## ¿Qué hace?

1. Recibe llamadas VoIP con **Asterisk** (PBX) y extensiones SIP.
2. **Python controla las llamadas por ARI**: contesta, crea un *bridge*, une cliente y agente y graba la conversación en `.wav`.
3. **Whisper** (local) transcribe el audio a texto.
4. Un **regex enmascara** los datos de tarjeta y se calcula un **puntaje de calidad** por palabras de cortesía.
5. Todo se guarda en **MongoDB** y se visualiza en un **dashboard Flask** con login y reproductor de audio.

---

## Arquitectura

```
Windows (softphones)                 Ubuntu VM (VirtualBox)
┌───────────────────┐   Host-only    ┌──────────────────────────────────────┐
│ Zoiper   · 6001   │  192.168.56.102│  call-controller.py (ARI)            │
│ Linphone · 6002   │ ─────────────► │        │ ARI 8088                     │
└───────────────────┘   SIP/RTP/web  │        ▼                             │
                                     │  ┌─── Docker Compose ─────────────┐  │
                                     │  │ Asterisk  MongoDB 4.4          │  │
                                     │  │ Redis 7   Dashboard Flask 5000 │  │
                                     │  └────────────────────────────────┘  │
                                     └──────────────────────────────────────┘
```

Flujo de una llamada: **marca 8000 → Asterisk/Stasis → bridge + grabación → Whisper → enmascarado + puntaje → MongoDB → dashboard**.

---

## Stack y versiones

| Herramienta | Versión | Rol |
|---|---|---|
| Ubuntu | 22.04.5 LTS | Sistema operativo de la VM |
| Asterisk | 18.10.0 LTS | Central telefónica (SIP / ARI) |
| PJSIP | módulo de Asterisk | Stack SIP (extensiones) |
| Docker + Compose | Engine + plugin | Orquestación de contenedores |
| MongoDB | 4.4 | Base NoSQL de transcripciones |
| Redis | 7-alpine | Cola / estado en memoria |
| Flask | Python | Dashboard web |
| Whisper | small (int8) | Transcripción de voz a texto |
| faster-whisper | — | Motor STT optimizado en CPU |
| Códec de audio | G.711 (ulaw, alaw) | Audio de la llamada |

## Puertos

| Puerto | Protocolo | Servicio |
|---|---|---|
| 5060 | UDP | Asterisk SIP (señalización) |
| 10000–10100 | UDP | Asterisk RTP (audio) |
| 8088 | TCP | Asterisk ARI (REST + WebSocket) |
| 5000 | TCP | Dashboard Flask |
| 27017 | TCP | MongoDB |
| 6379 | TCP | Redis |

---

## Cómo levantarlo

Requisitos: Ubuntu con **Docker** y **Docker Compose**, y **Python 3.10** en el host para el call-controller.

**1. Levantar los servicios base** (Asterisk, MongoDB, Redis, Dashboard):
```bash
docker compose up -d
```

**2. Arrancar el controlador de llamadas** (dejar esta terminal abierta):
```bash
cd call-controller
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python call-controller-bridge.py
```

**3. Hacer una llamada:** desde el softphone (ext. 6001) marcar **8000**, hablar y colgar.

**4. Procesar** (en otra terminal):
```bash
cd call-controller && source venv/bin/activate
python procesar.py
```

**5. Ver el resultado:** abrir `http://192.168.56.102:5000` (usuario `admin`, clave `admin123`).

### Comandos útiles de verificación
```bash
docker ps
docker exec -it marcacion_asterisk asterisk -rx "core show version"
docker exec -it marcacion_asterisk asterisk -rx "pjsip show endpoints"
curl -u ariuser:aripass http://localhost:8088/ari/asterisk/info
curl http://localhost:5000/health
```

---

## Estructura del proyecto

```
asistente-marcacion-inteligente/
├── docker-compose.yml
├── .env.example
├── telefonia/            # Configuración de Asterisk (Dockerfile + .conf)
│   ├── Dockerfile
│   ├── pjsip.conf        # Extensiones 6001 / 6002 (PJSIP, G.711)
│   ├── extensions.conf   # Dialplan + Stasis(8000)
│   ├── ari.conf          # Usuario ARI
│   ├── http.conf         # Puerto 8088
│   └── rtp.conf          # Rango RTP 10000-10100
├── call-controller/      # Control de llamadas y pipeline de IA
│   ├── call-controller.py         # Versión ARI simple (grabación de un canal)
│   ├── call-controller-bridge.py  # Versión con bridge (cliente + agente)
│   ├── procesar.py                # Whisper + enmascarado + MongoDB
│   ├── transcribir.py             # Prueba: audio a texto
│   ├── enmascarar.py              # Prueba: ocultar tarjeta + puntaje
│   └── requirements.txt
├── dashboard/            # Dashboard web (Flask)
│   ├── Dockerfile
│   ├── app.py            # Login + /health + /audio + lectura de MongoDB
│   ├── requirements.txt
│   └── templates/
│       ├── index.html
│       └── login.html
├── recordings/           # Grabaciones .wav (ignoradas por git)
└── docs/
    └── DOCUMENTACION.md
```

---

## Nota de seguridad

Las credenciales de este repositorio (`ariuser/aripass`, `admin/admin123`) son **de laboratorio**, para un entorno local aislado. En un despliegue real deben moverse a variables de entorno (ver `.env.example`) y usarse contraseñas fuertes, JWT/bcrypt para el dashboard y TLS/SRTP para las comunicaciones.

Las grabaciones (`recordings/*.wav`) **no se suben** al repositorio porque pueden contener datos sensibles.

---

## Estado y roadmap

**Funcionando (avance de laboratorio):** telefonía SIP, control por ARI, grabación con bridge, transcripción con Whisper, enmascarado de tarjeta, puntaje de calidad y dashboard con login.

**Roadmap a producción:** worker asíncrono real consumiendo la cola de Redis, base relacional MySQL/CDR, pruebas de carga (SIPp) y métricas MOS/WER, monitoreo con Prometheus + Grafana, respaldos automáticos, TLS/SRTP, MFA, alta disponibilidad y clustering.

> **Nota sobre los archivos:** los scripts de `call-controller/` (`call-controller.py`, `procesar.py`, `transcribir.py`, `enmascarar.py`) y `pjsip.conf` provienen del proyecto real. `docker-compose.yml`, los demás `.conf`, `call-controller-bridge.py` y el `dashboard/` fueron reconstruidos a partir de la documentación del avance; si tu versión local difiere, reemplázalos por los tuyos.

---

## Autores

Grupo 05 — **Lady Loayza · Jose Castro · Andy Vergara**
