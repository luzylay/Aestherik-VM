# Documentación técnica — Call Center Inteligente

## 1. Objetivo
Convertir una PBX básica en un Call Center Inteligente: contestar y controlar llamadas por software,
grabarlas, transcribirlas con IA, ocultar datos sensibles y analizarlas en un dashboard.

## 2. Componentes
- **Asterisk (PBX):** registra las extensiones SIP y enruta las llamadas. Stack SIP: PJSIP.
- **ARI (Asterisk REST Interface):** REST + WebSocket para que Python controle las llamadas.
- **call-controller (Python):** escucha eventos de Asterisk (Stasis), contesta, crea un bridge,
  une cliente y agente y graba.
- **Whisper (faster-whisper, small, int8):** transcribe el audio a texto, local y offline.
- **Enmascarado:** un regex detecta 13–16 dígitos y reemplaza la tarjeta por [TARJETA OCULTA].
- **Puntaje de calidad:** cuenta palabras de cortesía (25 pts por frase, tope 100).
- **MongoDB:** guarda transcripciones y metadatos.
- **Redis:** cola/estado en memoria (desplegado; worker asíncrono en roadmap).
- **Dashboard Flask:** login por sesión, tabla de llamadas y reproductor de audio.

## 3. Flujo de la llamada
1. El softphone marca 8000.
2. Asterisk entrega la llamada a la app Stasis (callcenter-app) por ARI.
3. call-controller crea un mixing bridge, mete al cliente y graba.
4. Origina una llamada al agente 6001 y lo une al bridge.
5. Al colgar, procesar.py transcribe el .wav con Whisper.
6. Se enmascara la tarjeta y se calcula el puntaje.
7. Se guarda en MongoDB (colecciones calls y transcriptions).
8. El dashboard muestra la llamada y permite reproducir el audio.

## 4. Decisiones técnicas
- **MongoDB 4.4** (no 7): Mongo 5.0+ requiere instrucciones AVX en el CPU; la VM de VirtualBox
  no siempre las expone, por eso se usó la 4.4 por compatibilidad.
- **Ubuntu como base de Asterisk** (no Debian): el paquete asterisk no tenía candidato en
  debian:bookworm-slim; Ubuntu 22.04 sí lo trae en repos (Asterisk 18.10.0).
- **Whisper small + int8:** balance precisión (~92%) / velocidad, corre en CPU sin GPU.
- **ARI en lugar de AGI:** ARI permite control asíncrono bidireccional (bridge, grabación,
  originar llamadas) desde un programa externo.
- **Red Host-only (192.168.56.102):** IP fija alcanzable desde Windows; NAT (10.0.2.15) solo
  da internet a la VM.
- **Códec G.711 (ulaw/alaw):** audio de alta calidad, mejora la precisión de la transcripción.
- **Grabación mono:** el mixing bridge mezcla las dos voces en un solo canal.

## 5. Incidencias resueltas durante el desarrollo
- DNS de la VM no resolvía repositorios -> se usó NAT temporal para instalar paquetes.
- Dashboard reiniciaba por error en app.py (Flask(name)) -> se corrigió a Flask("dashboard").
- Asterisk no instalaba en Debian -> se cambió la imagen base a ubuntu:22.04.
- Zoiper registraba con IP pública -> parámetros NAT en PJSIP (rtp_symmetric, force_rport,
  rewrite_contact).
