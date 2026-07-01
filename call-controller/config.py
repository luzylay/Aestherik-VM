import os

# Intentar cargar .env para desarrollo local si python-dotenv está disponible
try:
    from dotenv import load_dotenv
    # Subir un nivel para encontrar el .env en la raíz si es necesario
    for path in ['.env', '../.env', '../../.env']:
        if os.path.exists(path):
            load_dotenv(dotenv_path=path)
            break
except ImportError:
    pass

# Configuración de Asterisk ARI
ARI_USER = os.environ.get("ARI_USER", "ariuser")
ARI_PASS = os.environ.get("ARI_PASS", "aripass")
ARI_HOST = os.environ.get("ARI_HOST", "localhost")
ARI_PORT = int(os.environ.get("ARI_PORT", 8088))
APP_NAME = os.environ.get("APP_NAME", "callcenter-app")
AGENTE = os.environ.get("AGENTE", "PJSIP/6001")

# Configuración de NoSQL (MongoDB)
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:admin123@localhost:27017/marcacion_db?authSource=admin")

# Configuración de Redis
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

# Directorio de Grabaciones
RECORDINGS_DIR = os.environ.get("RECORDINGS_DIR", "../recordings")
