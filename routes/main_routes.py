from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime

main_bp = Blueprint('main', __name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

UPLOAD_SOLICITUDES = 'static/uploads/solicitudes'
os.makedirs(UPLOAD_SOLICITUDES, exist_ok=True)

UPLOAD_PAGOS = 'static/uploads/pagos'
os.makedirs(UPLOAD_PAGOS, exist_ok=True)

@main_bp.route('/')
def index():
    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()

    # --- Obtener todas las convocatorias ---
    cursor.execute("SELECT nombre, descripcion, fecha_inicio, fecha_fin FROM convocatorias")
    todas = cursor.fetchall()

    # --- Obtener requisitos ---
    cursor.execute("SELECT contenido FROM requisitos")
    requisitos = [fila[0] for fila in cursor.fetchall()]

    # --- Obtener documentos ---
    cursor.execute("SELECT descripcion FROM documentos")    
    documentos = [fila[0] for fila in cursor.fetchall()]

    # --- Obtener solicitudes de pago ---
    cursor.execute("SELECT * FROM pago ORDER BY id DESC")
    pagos = cursor.fetchall()    

    conexion.close()

    # --- Procesar estado de convocatorias ---
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

    # --- Renderizar página principal ---
    return render_template(
        'index.html',
        convocatorias=convocatorias_info,
        requisitos=requisitos,
        documentos=documentos, pagos=pagos
    )


@main_bp.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        try:
            # Capturar datos del formulario
            matricula = request.form['matricula']
            nombre = request.form['nombre']
            apellidos = request.form['apellidos']
            curp = request.form['curp']
            nss = request.form.get('nss')
            carrera = request.form.get('carrera')
            beca = request.form.get('beca')
            porcentaje_cursado = request.form.get('porcentaje_cursado')
            materias_reprobadas = request.form.get('materias_reprobadas')
            promedio = request.form.get('promedio')
            telefono = request.form['telefono']
            correo = request.form['correo']
            actividades = request.form.get('actividades')
            horario = request.form.get('horario')
            area = request.form.get('area')
            coordinador = request.form.get('coordinador')
            pdf = request.files.get('pdf')  


            # Capturar archivo PDF
            nombre_pdf = None
            if pdf and pdf.filename != '' and pdf.filename.endswith('.pdf'):
                nombre_seguro = secure_filename(pdf.filename)
                # Renombrar para evitar duplicados: matricula + timestamp + nombre
                nombre_pdf = f"{matricula}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{nombre_seguro}"
                pdf.save(os.path.join(UPLOAD_SOLICITUDES, nombre_pdf))

            # Guardar en la base de datos
            conexion = sqlite3.connect('becas.db')
            cursor = conexion.cursor()
            cursor.execute('''
                INSERT INTO solicitudes (
                    matricula, nombre, apellidos, curp, nss, carrera, beca, 
                    porcentaje_cursado, materias_reprobadas, promedio, 
                    telefono, correo, actividades, horario, area, coordinador, pdf, fecha_registro,estatus
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now','localtime'), 'Recibida')
            ''', (
                matricula, nombre, apellidos, curp, nss, carrera, beca,
                porcentaje_cursado, materias_reprobadas, promedio,
                telefono, correo, actividades, horario, area, coordinador,
                nombre_pdf
            ))

            conexion.commit()
            conexion.close()

            flash("Tu solicitud fue enviada correctamente")
            return redirect(url_for('main.formulario'))
        
        except sqlite3.IntegrityError:
            flash(" Ya existe una solicitud con esa matrícula.")
            return redirect(url_for('main.formulario'))
        except Exception as e:
            flash(f" Error al enviar la solicitud: {e}")
            return redirect(url_for('main.formulario'))
        
    return render_template('formulario.html')



@main_bp.route('/resultado', methods=['GET', 'POST'])
def resultado():
    solicitud = None

    if request.method == 'POST':
        matricula = request.form['matricula']

        conexion = sqlite3.connect('becas.db')
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre, apellidos, matricula, estatus, carrera, beca,comentario_admin FROM solicitudes WHERE matricula = ? ", (matricula,))
        solicitud = cursor.fetchone()

        cursor.execute("SELECT nombre, apellidos, matricula,estatus, comentario_admin FROM pago WHERE matricula = ? ", (matricula,))
        pagos = cursor.fetchall()
        
        conexion.close()

        if solicitud:
            return render_template('resultado.html', solicitud=solicitud, pagos=pagos)
        else:
            flash("No se encontró ninguna solicitud asociada a esa matricula.")
            return redirect(url_for('main.resultado'))

    return render_template('resultado.html', solicitud=None)


@main_bp.route('/formulario_pago', methods=['GET', 'POST'])
def formulario_pago():
    if request.method == 'POST':
        try:
            # --- Capturar datos del formulario de pago ---
            nombre = request.form['nombre']
            apellidos = request.form['apellidos']
            matricula = request.form['matricula']
            archivo_pago = request.files.get('archivo_pago')

            # --- Capturar archivo PDF ---
            nombre_archivo = None
            if archivo_pago and archivo_pago.filename != '' and archivo_pago.filename.endswith('.pdf'):
                nombre_seguro = secure_filename(archivo_pago.filename)
                # Renombrar para evitar duplicados: matricula + timestamp + nombre
                nombre_archivo = f"{matricula}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{nombre_seguro}"
                archivo_pago.save(os.path.join(UPLOAD_PAGOS, nombre_archivo))

            # --- Guardar en la base de datos ---
            conexion = sqlite3.connect('becas.db')
            cursor = conexion.cursor()
            cursor.execute('''
                INSERT INTO pago (nombre, apellidos, matricula, archivo_pago)
                VALUES (?, ?, ?, ?)
            ''', (
                nombre, apellidos, matricula, nombre_archivo
            ))
            conexion.commit()
            conexion.close()

            flash("Tu formulario de pago fue enviado correctamente")
            return redirect(url_for('main.formulario_pago'))

        except sqlite3.IntegrityError:
            flash("Ya existe un formulario de pago con esa matrícula.")
            return redirect(url_for('main.formulario_pago'))
        except Exception as e:
            flash(f"Error al enviar el formulario de pago: {e}")
            return redirect(url_for('main.formulario_pago'))

    return render_template('formulario-pago.html')


