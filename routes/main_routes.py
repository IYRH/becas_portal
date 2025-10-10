from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename

main_bp = Blueprint('main', __name__)

# Carpeta donde se guardarán los PDFs
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/solicitud', methods=['GET', 'POST'])
def solicitud():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        curp = request.form['curp']
        correo = request.form['correo']
        telefono = request.form['telefono']
        nss = request.form['nss']
        porcentaje = request.form['porcentaje']
        carrera = request.form['carrera']
        beca = request.form['beca']
        pdf = request.files['pdf']

        # Validar que el PDF exista
        if pdf and pdf.filename.endswith('.pdf'):
            filename = secure_filename(pdf.filename)
            pdf_path = os.path.join(UPLOAD_FOLDER, filename)
            pdf.save(pdf_path)
        else:
            flash("Por favor sube un archivo PDF válido.")
            return redirect(url_for('main.solicitud'))

        # Guardar en la base de datos
        conexion = sqlite3.connect('becas.db')
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO solicitudes (nombre, curp, correo, telefono, nss, porcentaje_cursado, carrera, beca, pdf)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, curp, correo, telefono, nss, porcentaje, carrera, beca, pdf_path))
        conexion.commit()
        conexion.close()

        flash("Tu solicitud fue enviada correctamente. ✅")
        return redirect(url_for('main.solicitud'))

    return render_template('formulario.html')
