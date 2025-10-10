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
    return render_template('index.html')

@main_bp.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
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
            (nombre, apellidos, curp, correo, telefono, nss, porcentaje_cursado, carrera, beca, pdf, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, apellidos, curp, correo, telefono, nss, porcentaje, carrera, beca, pdf_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conexion.commit()
        conexion.close()

        flash("Tu solicitud fue enviada correctamente ✅")
        return redirect(url_for('main.formulario'))

    return render_template('formulario.html')
