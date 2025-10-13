from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime

main_bp = Blueprint('main', __name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@main_bp.route('/')
def index():
    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()

    # Obtener todas las convocatorias
    cursor.execute("SELECT nombre, descripcion, fecha_inicio, fecha_fin FROM convocatorias")
    todas = cursor.fetchall()
    conexion.close()

    hoy = datetime.now().date()

    convocatorias_info = []
    for nombre, descripcion, inicio, fin in todas:
        if inicio and fin:
            inicio_dt = datetime.strptime(inicio, "%Y-%m-%d").date()
            fin_dt = datetime.strptime(fin, "%Y-%m-%d").date()
            if inicio_dt <= hoy <= fin_dt:
                estado = "Activa"
            elif hoy < inicio_dt:
                estado = "Próxima"
            else:
                estado = "Inactiva"
        else:
            estado = "Sin fechas"

        convocatorias_info.append((nombre, descripcion, inicio, fin, estado))

    return render_template('index.html', convocatorias=convocatorias_info)

@main_bp.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        matricula = request.form['matricula']
        curp = request.form.get('curp', '') 
        correo = request.form['correo']
        telefono = request.form['telefono']
        nss = request.form['nss']
        porcentaje = request.form['porcentaje_materias']
        carrera = request.form['carrera']
        beca = request.form.get('beca', '')
        pdf = request.files.get('pdf')

        # Validar PDF
        pdf_path = None
        if pdf and pdf.filename.endswith('.pdf'):
            filename = secure_filename(pdf.filename)
            pdf_path = os.path.join(UPLOAD_FOLDER, filename)
            pdf.save(pdf_path)

        # Guardar en la base de datos
        conexion = sqlite3.connect('becas.db')
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO solicitudes 
            (nombre, apellidos, matricula, curp, correo, telefono, nss, porcentaje_cursado, carrera, beca, pdf, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, apellidos, matricula, curp, correo, telefono, nss, porcentaje, carrera, beca, pdf_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conexion.commit()
        conexion.close()

        flash("Tu solicitud fue enviada correctamente")
        return redirect(url_for('main.formulario'))

    return render_template('formulario.html')

@main_bp.route('/resultado', methods=['GET', 'POST'])
def resultado():
    if request.method == 'POST':
        matricula = request.form['matricula']

        conexion = sqlite3.connect('becas.db')
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre, apellidos, curp, carrera, estatus, fecha_registro FROM solicitudes WHERE matricula = ?", (matricula,))
        solicitud = cursor.fetchone()
        conexion.close()

        if solicitud:
            return render_template('resultado.html', solicitud=solicitud)
        else:
            flash("No se encontró ninguna solicitud asociada a esa matricula.")
            return redirect(url_for('main.resultado'))

    return render_template('resultado.html', solicitud=None)

