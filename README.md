# Call Center Inteligente con IA (Aestherik-VM)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Docker: Compose](https://img.shields.io/badge/Docker-Compose-cyan.svg)](https://www.docker.com/)
[![Asterisk: 18.10.0](https://img.shields.io/badge/Asterisk-18.10.0_LTS-orange.svg)](https://www.asterisk.org/)
[![Whisper: Small/int8](https://img.shields.io/badge/AI_Transcription-Whisper_small-green.svg)](https://github.com/openai/whisper)

**Aestherik-VM** es una plataforma de telefonía inteligente y análisis de calidad basada en Inteligencia Artificial. Conecta flujos de comunicación de voz tradicionales con procesamiento cognitivo moderno en tiempo real: graba llamadas bidireccionales, las transcribe mediante Whisper de forma local y offline, oculta automáticamente datos sensibles (como números de tarjetas de crédito) y califica la atención al cliente según el uso de palabras de cortesía.

---

## 📖 Índice

- [Vista General para Usuarios](#-vista-general-para-usuarios)
- [Arquitectura Técnica](#%EF%B8%F0-arquitectura-técnica)
- [Características Principales](#-características-principales)
- [Tecnologías y Versiones](#-tecnologías-y-versiones)
- [Guía de Instalación y Despliegue](#-guía-de-instalación-y-despliegue)
- [Estructura del Repositorio](#-estructura-del-repositorio)
- [Seguridad en Producción](#-seguridad-en-producción)
- [Colaboración y Licencia](#-colaboración-y-licencia)

---

## 👥 Vista General para Usuarios

### ¿Qué problema resuelve este sistema?
En los centros de atención al cliente (Call Centers) tradicionales, supervisar las llamadas para verificar la calidad y el cumplimiento normativo suele ser un proceso manual y costoso. Además, las grabaciones pueden almacenar información crítica de los clientes, como números de tarjetas de crédito, lo que expone a la empresa a multas y brechas de seguridad (incumplimiento de normativas como PCI-DSS).

### ¿Cómo ayuda Aestherik-VM?
1. **Atiende Automáticamente**: Permite canalizar llamadas telefónicas hacia agentes y supervisar la conversación sin fricciones.
2. **Transcripción Local Inteligente**: Convierte la voz de la llamada a texto escrito de manera 100% interna y privada (sin enviar audios a internet).
3. **Protección de Datos Activa**: Si un cliente menciona los dígitos de su tarjeta bancaria, el sistema los detecta y los reemplaza instantáneamente por un texto seguro antes de guardarlos.
4. **Calificación Automatizada**: Evalúa el desempeño del agente otorgando una puntuación basada en la amabilidad y cortesía expresadas durante el diálogo.
5. **Panel de Control Intuitivo**: Un supervisor puede acceder mediante una contraseña segura a una interfaz web limpia para ver resúmenes del día, buscar llamadas específicas y escuchar los audios correspondientes.

---

## ⚙️ Arquitectura Técnica

El sistema está diseñado de manera modular y asíncrona mediante microservicios Dockerizados para asegurar escalabilidad y estabilidad bajo carga:

```
                                      FLUJO ASÍNCRONO DEL SISTEMA
                                      
    +------------+                  +------------------+                   +--------------------+
    | Softphone  |   SIP/RTP        |   Asterisk PBX   |                   |    Nginx Proxy     |
    | (Zoiper)   | <--------------> | (Contenedor VoIP)|                   | (HTTPS / Port 443) |
    +------------+                  +------------------+                   +--------------------+
                                             |                                       |
                                             | WebSocket / REST                      | Carga Web
                                             v                                       v
                                    +------------------+                   +--------------------+
                                    | call-controller  |                   |   Dashboard Web    |
                                    | (ARI - Python)   |                   |    (Flask App)     |
                                    +------------------+                   +--------------------+
                                             |                                       |
                                             | Encola Metadatos                      | Consulta Datos
                                             v                                       v
    +------------+                  +------------------+                   +--------------------+
    | Grabación  | <--------------  |   Redis Queue    |                   |      MongoDB       |
    | (.wav)     |  Lectura Audio   |  (Cola de Tareas)|                   | (Base de Datos NoSQL)|
    +------------+                  +------------------+                   +--------------------+
          ^                                  |                                       ^
          |                                  | Desencola Tarea                       | Guarda Resultados
          +----------------------------------+---------------------------------------+
                                             v
                                    +------------------+
                                    |  Worker Whisper  |
                                    | (Procesador IA)  |
                                    +------------------+
```

### Detalle del Flujo de Procesamiento:
1. **Llamada de Entrada**: El cliente marca la extensión `8000`. Asterisk entrega la llamada a la aplicación en Python (`callcenter-app`) a través de la interfaz **ARI (Asterisk REST Interface)**.
2. **Grabación Estéreo y Conexión**: El controlador crea un *bridge* de mezcla, une al cliente con el agente (`6001`), y graba la sesión en un archivo `.wav`.
3. **Encolamiento en Redis**: Al colgar la llamada, el controlador calcula la duración y envía los metadatos a una cola de mensajes en **Redis**.
4. **Procesamiento Asíncrono (Worker)**: Un proceso de fondo (Worker) saca la tarea de la cola, lee el archivo de audio, lo transcribe utilizando **Whisper Model (small/int8)** en CPU, enmascara las tarjetas con expresiones regulares y puntúa la llamada.
5. **Persistencia e Interfaz**: Los datos procesados se almacenan en **MongoDB** y el supervisor los visualiza a través del **Dashboard Web** asegurado por un proxy **Nginx (HTTPS)**.

---

## ✨ Características Principales

*   **Telefonía VoIP Avanzada**: Extensiones SIP configuradas en PJSIP con soporte para códec G.711 de alta fidelidad.
*   **Procesamiento Desacoplado**: El uso de Redis evita que el controlador de llamadas de Asterisk se bloquee o enlentezca mientras realiza la transcripción de inteligencia artificial.
*   **Seguridad y Privacidad SSL/TLS**: Conexión HTTPS segura y redirección HTTP automática gestionada por Nginx.
*   **Enmascarado Inteligente**: Algoritmo robusto de expresiones regulares que detecta y protege secuencias de 13 a 16 dígitos.
*   **Dashboard Moderno (Dark Mode)**: Interfaz de usuario diseñada con estética ejecutiva oscura, tarjetas de estado en tiempo real, filtro interactivo instantáneo y reproductor web nativo.

---

## 🛠️ Tecnologías y Versiones

| Herramienta | Versión | Rol en el Proyecto |
| :--- | :--- | :--- |
| **Asterisk** | 18.10.0 LTS | Centralita telefónica (conmuta y une canales) |
| **faster-whisper**| `small` (int8) | Reconocimiento de voz local optimizado para CPU |
| **MongoDB** | 4.4 | Base de datos NoSQL persistente para reportes |
| **Redis** | 7-alpine | Cola de mensajes rápida en memoria |
| **Flask** | Python 3.10 | Framework para el Dashboard de administración |
| **Nginx** | Alpine | Proxy inverso con soporte para SSL/TLS |

---

## 🚀 Guía de Instalación y Despliegue

### Requisitos Previos
- Servidor o máquina virtual con **Ubuntu 22.04 LTS** (o similar).
- **Docker** y **Docker Compose** instalados.
- **Python 3.10+** instalado en el host local.

### Paso 1: Clonar y Configurar
Copia el archivo de variables de entorno de ejemplo a su nombre definitivo:
```bash
cp .env.example .env
```

### Paso 2: Generar Certificados de Seguridad
Genera de manera automática los certificados SSL/TLS autofirmados requeridos por Nginx para cifrar la comunicación web:
```bash
python scripts/generate_certs.py
```

### Paso 3: Levantar los Contenedores
Inicia y compila el conjunto de microservicios con Docker Compose:
```bash
docker compose up --build -d
```
*Este paso descargará e inicializará MongoDB, Redis, el Worker de Whisper, Nginx y el Dashboard.*

### Paso 4: Arrancar el Controlador Telefónico (ARI)
En la máquina host (o tu terminal local), ejecuta el controlador que escuchará los eventos de llamada de Asterisk:
```bash
cd call-controller
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python call-controller-bridge.py
```

### Paso 5: Probar el Sistema
1. Conecta tus softphones (como **Zoiper** o **Linphone**) a las extensiones `6001` o `6002` (Credenciales por defecto en `telefonia/pjsip.conf`).
2. Marca el número de Stasis **`8000`**. Habla y cuelga.
3. Abre tu navegador e ingresa a **`https://localhost`** (o la dirección IP de tu servidor).
4. Introduce el usuario `admin` y la contraseña `admin123`.
5. ¡Listo! Observarás el registro de llamadas procesado en tiempo real con su respectiva puntuación y transcripción segura.

---

## 📁 Estructura del Repositorio

```
asistente-marcacion-inteligente/
├── docker-compose.yml       # Orquestador de microservicios
├── .env.example             # Plantilla de variables de entorno
├── LICENSE                  # Licencia de código abierto MIT
├── CONTRIBUTING.md          # Pautas para contribuciones de código
├── CODE_OF_CONDUCT.md       # Normas de convivencia del proyecto
├── SECURITY.md              # Políticas y reporte de vulnerabilidades
├── certs/                   # Certificados SSL locales (ignorado por Git)
├── telefonia/               # Archivo de construcción y configs de Asterisk
├── call-controller/         # Scripts de control de llamadas y Worker de Whisper
│   ├── config.py            # Carga variables de entorno para scripts
│   ├── worker.py            # Escucha Redis y transcribe con Whisper
│   ├── Dockerfile.worker    # Construcción del contenedor del Worker
│   └── call-controller-bridge.py # Controlador principal del puente de llamadas
├── dashboard/               # Servidor web Flask
│   ├── app.py               # API web y vistas
│   └── templates/           # Vistas de login e index HTML rediseñadas
├── nginx/                   # Proxy Nginx con HTTPS
└── recordings/              # Almacenamiento temporal de llamadas (ignorado por Git)
```

---

## 🔒 Seguridad en Producción

> [!WARNING]
> **Credenciales por Defecto**: Las contraseñas de este repositorio (`admin123`, `aripass`) son exclusivamente para entornos locales de pruebas de laboratorio. **No las uses en servidores públicos**. Reemplázalas en el archivo `.env` por credenciales seguras.

> [!NOTE]
> **Datos de Tarjetas**: El enmascarado regex elimina los datos sensibles antes de guardarlos en MongoDB. Sin embargo, para mayor cumplimiento normativo, se recomienda deshabilitar el guardado de los audios físicos en producción, o cifrar el volumen de almacenamiento de `recordings/`.

---

## 🤝 Colaboración y Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para obtener más detalles. Si deseas colaborar con correcciones de errores, sugerencias o nuevas implementaciones, por favor consulta nuestra guía en [CONTRIBUTING.md](CONTRIBUTING.md).

---
*Aestherik-VM: Elevando la telefonía inteligente con IA y seguridad activa.*
