# Dashboard Web - Aplicación de Administración del Call Center
# Muestra estadísticas, transcripciones enmascaradas y permite escuchar grabaciones.
import os
from flask import (Flask, render_template, request, redirect,
                   url_for, session, send_from_directory, jsonify)
from pymongo import MongoClient
import redis
import config

app = Flask("dashboard")
app.secret_key = config.DASHBOARD_SECRET_KEY

def get_db():
    client = MongoClient(config.MONGO_URI)
    return client.get_default_database() # Obtiene la DB configurada en la URI (marcacion_db)

@app.route("/health")
def health():
    estado = {"status": "ok", "services": {}}
    # Probar MongoDB
    try:
        get_db().command("ping")
        estado["services"]["mongodb"] = "connected"
    except Exception as e:
        estado["status"] = "degraded"
        estado["services"]["mongodb"] = f"error: {str(e)}"
    
    # Probar Redis
    try:
        r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
        r.ping()
        estado["services"]["redis"] = "connected"
    except Exception as e:
        estado["status"] = "degraded"
        estado["services"]["redis"] = f"error: {str(e)}"
        
    return jsonify(estado)

@app.route("/login", methods=["GET", "POST"])
def login():
    # Si ya está logueado, redirigir
    if session.get("logueado"):
        return redirect(url_for("index"))
        
    if request.method == "POST":
        usuario_input = request.form.get("usuario")
        clave_input = request.form.get("clave")
        
        if usuario_input == config.DASHBOARD_USER and clave_input == config.DASHBOARD_PASS:
            session["logueado"] = True
            return redirect(url_for("index"))
        return render_template("login.html", error="Credenciales inválidas")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if not session.get("logueado"):
        return redirect(url_for("login"))
    
    # Obtener llamadas de MongoDB
    db = get_db()
    llamadas = list(db["calls"].find().sort("created_at", -1))
    
    # Calcular estadísticas básicas para el dashboard
    total_calls = len(llamadas)
    
    if total_calls > 0:
        avg_score = round(sum(c.get("puntaje", 0) for c in llamadas) / total_calls, 1)
        redacted_calls = sum(1 for c in llamadas if c.get("contiene_tarjeta", False) or "[TARJETA" in c.get("texto_seguro", ""))
        pct_safe = round(((total_calls - redacted_calls) / total_calls) * 100, 1)
    else:
        avg_score = 0.0
        redacted_calls = 0
        pct_safe = 100.0

    stats = {
        "total_calls": total_calls,
        "avg_score": avg_score,
        "redacted_calls": redacted_calls,
        "pct_safe": pct_safe
    }

    return render_template("index.html", llamadas=llamadas, stats=stats)

@app.route("/audio/<nombre>")
def audio(nombre):
    if not session.get("logueado"):
        return redirect(url_for("login"))
    # Sanitizar nombre de archivo básico por seguridad
    nombre_seguro = os.path.basename(nombre)
    return send_from_directory(config.RECORDINGS_DIR, nombre_seguro)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
