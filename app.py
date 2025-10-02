from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os

app = Flask(__name__)

# Crear base de datos si no existe
def init_db():
    with sqlite3.connect("becas.db") as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            matricula TEXT,
            correo TEXT,
            documento TEXT
        )
        """)
        conn.commit()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/solicitar", methods=["POST"])
def solicitar():
    nombre = request.form["nombre"]
    matricula = request.form["matricula"]
    correo = request.form["correo"]
    documento = request.files["documento"]

    # Guardar archivo PDF
    filename = f"static/docs/{matricula}.pdf"
    os.makedirs("static/docs", exist_ok=True)
    documento.save(filename)

    # Guardar en la base de datos
    with sqlite3.connect("becas.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO solicitudes (nombre, matricula, correo, documento) VALUES (?, ?, ?, ?)",
                  (nombre, matricula, correo, filename))
        conn.commit()

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
