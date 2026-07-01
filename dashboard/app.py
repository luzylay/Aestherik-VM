# NOTA: version RECONSTRUIDA del dashboard segun la mejora descrita
# (login por sesion, endpoint /health, reproductor de audio y lectura de MongoDB).
import os
from flask import (Flask, render_template, request, redirect,
                   url_for, session, send_from_directory, jsonify)
from pymongo import MongoClient
import redis

app = Flask("dashboard")
app.secret_key = "clave_secreta_para_demo"

# Credenciales de laboratorio (cambiar en produccion)
USUARIO = "admin"
CLAVE = "admin123"

MONGO_URI = "mongodb://admin:admin123@mongo:27017/marcacion_db?authSource=admin"
RECORDINGS_DIR = "/call-controller"


def get_db():
    return MongoClient(MONGO_URI)["marcacion_db"]


@app.route("/health")
def health():
    estado = {"status": "ok"}
    try:
        get_db().command("ping")
        estado["mongo"] = "connected"
    except Exception:
        estado["mongo"] = "error"
    try:
        redis.Redis(host="redis", port=6379).ping()
        estado["redis"] = "connected"
    except Exception:
        estado["redis"] = "error"
    return jsonify(estado)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("usuario") == USUARIO and request.form.get("clave") == CLAVE:
            session["logueado"] = True
            return redirect(url_for("index"))
        return render_template("login.html", error="Credenciales incorrectas")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def index():
    if not session.get("logueado"):
        return redirect(url_for("login"))
    llamadas = list(get_db()["calls"].find().sort("created_at", -1))
    return render_template("index.html", llamadas=llamadas)


@app.route("/audio/<nombre>")
def audio(nombre):
    if not session.get("logueado"):
        return redirect(url_for("login"))
    return send_from_directory(RECORDINGS_DIR, nombre)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
