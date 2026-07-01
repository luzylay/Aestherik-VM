import os

# Intentar cargar .env para desarrollo local si python-dotenv está disponible
try:
    from dotenv import load_dotenv
    for path in ['.env', '../.env', '../../.env']:
        if os.path.exists(path):
            load_dotenv(dotenv_path=path)
            break
except ImportError:
    pass

# Configuración de NoSQL (MongoDB)
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:admin123@mongo:27017/marcacion_db?authSource=admin")

# Configuración de Redis
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

# Directorio de Grabaciones
RECORDINGS_DIR = os.environ.get("RECORDINGS_DIR", "/call-controller")

# Configuración del Dashboard
DASHBOARD_SECRET_KEY = os.environ.get("DASHBOARD_SECRET_KEY", "clave_secreta_para_demo")
DASHBOARD_USER = os.environ.get("DASHBOARD_USER", "admin")
DASHBOARD_PASS = os.environ.get("DASHBOARD_PASS", "admin123")
