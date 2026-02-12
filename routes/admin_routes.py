from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
import sqlite3
from datetime import datetime
from openpyxl import Workbook
from werkzeug.security import generate_password_hash, check_password_hash
import io
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
DB = 'becas.db'

# Credenciales del administrador
#ADMIN_USER = "admin"
#ADMIN_PASS = "12345"

# Página de login
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['password']

        conexion = sqlite3.connect('becas.db')
        cursor = conexion.cursor()

        cursor.execute("SELECT id, username, password_hash FROM admin WHERE username = ?", (username,))
        admin = cursor.fetchone()

        conexion.close()

        if admin and check_password_hash(admin[2], password):
            session['admin_id'] = admin[0]
            session['admin_username'] = admin[1]
            flash("Bienvenido administrador ✅")
            return redirect(url_for('admin.panel'))
        else:
            flash("Usuario o contraseña incorrectos ❌")
            return redirect(url_for('admin.login'))

    return render_template('admin_login.html')



# Cerrar sesión
@admin_bp.route('/logout')
def logout():
    session.pop('admin', None)
    flash("Sesión cerrada correctamente.")
    return redirect(url_for('admin.login'))

# Panel principal (requiere sesión)
@admin_bp.route('/panel', methods=['GET', 'POST'])
def panel():
    if not session.get('admin_id'):
        flash("Debes iniciar sesión para acceder al panel.")
        return redirect(url_for('admin.login'))

    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()

    if request.method == 'POST':
        tipo = request.form.get('tipo')

        # --- Actualización de solicitudes (estatus + comentario) ---
        if tipo == 'solicitud':
            solicitud_id = request.form.get('id')
            estatus = request.form.get('estatus')
            comentario = request.form.get('comentario_admin')
            print("FORM DATA:", dict(request.form))

            if solicitud_id and estatus:
                cursor.execute('''
                    UPDATE solicitudes
                    SET estatus = ?, comentario_admin = ?
                    WHERE id = ?
                ''', (estatus, comentario, solicitud_id))
                conexion.commit()
                flash(" Solicitud actualizada correctamente.")
            else:
                flash(" Error: ID de solicitud o estatus no proporcionados.")

        # --- Actualizacion de solicitudes de pago ---
        elif tipo == 'pago':
            pago_id = request.form.get('id')
            estatus = request.form.get('estatus')
            comentario = request.form.get('comentario_admin')

            if pago_id and estatus:
                cursor.execute('''
                    UPDATE pago
                    SET estatus = ?, comentario_admin = ?
                    WHERE id = ?
                ''', (estatus, comentario, pago_id))
                conexion.commit()
                flash(" Solicitud de pago actualizada correctamente.")
            else:
                flash(" Error: ID de solicitud de pago o estatus no proporcionados.")

        # --- Actualización de convocatorias (fechas) ---
        elif tipo == 'convocatoria':
            convocatoria_id = request.form.get('id')
            fecha_inicio = request.form.get('fecha_inicio')
            fecha_fin = request.form.get('fecha_fin')

            if convocatoria_id:
                cursor.execute('''
                    UPDATE convocatorias
                    SET fecha_inicio = ?, fecha_fin = ?
                    WHERE id = ?
                ''', (fecha_inicio, fecha_fin, convocatoria_id))
                conexion.commit()
                flash(" Fechas de convocatoria actualizadas correctamente.")
            else:
                flash(" Error: ID de convocatoria no proporcionado.")

        # --- Actualización de requisitos ---
        elif tipo == 'requisito':
            req_id = request.form.get('id')
            contenido = request.form.get('contenido')

            if req_id and contenido:
                cursor.execute('UPDATE requisitos SET contenido = ? WHERE id = ?', (contenido, req_id))
                conexion.commit()
                flash("Requisito actualizado correctamente.")
            elif contenido and not req_id:
                cursor.execute('INSERT INTO requisitos (contenido) VALUES (?)', (contenido,))
                conexion.commit()
                flash("Nuevo requisito agregado.")
            else:
                flash("Error: no se proporcionó información válida para el requisito.")

        elif tipo == 'eliminar_requisito':
            req_id = request.form.get('id')
            if req_id:
                cursor.execute('DELETE FROM requisitos WHERE id = ?', (req_id,))
                conexion.commit()
                flash("Requisito eliminado correctamente ")

        # --- Actualización de documentos ---     
        elif tipo == 'documento':
            doc_id = request.form.get('id')
            descripcion = request.form.get('descripcion')

            if doc_id and descripcion:
                cursor.execute('UPDATE documentos SET descripcion = ? WHERE id = ?', (descripcion, doc_id))
                conexion.commit()
                flash("Documento actualizado correctamente.")
            elif descripcion and not doc_id:
                cursor.execute('INSERT INTO documentos (descripcion) VALUES (?)', (descripcion,))
                conexion.commit()
                flash("Nuevo documento agregado.")
            else:
                flash("Error: no se proporcionó información válida para el documento.")
        
        elif tipo == 'eliminar_documento':
            doc_id = request.form.get('id')
            if doc_id:
                cursor.execute('DELETE FROM documentos WHERE id = ?', (doc_id,))
                conexion.commit()
                flash("Documento eliminado correctamente")
            else:
                flash("Error: no se proporcionó un ID válido para eliminar.")


        

    # Obtener solicitudes 
    cursor.execute("SELECT id, nombre, apellidos,matricula , correo, telefono, materias_reprobadas, carrera, porcentaje_cursado, pdf, estatus, comentario_admin FROM solicitudes ORDER BY fecha_registro DESC")
    solicitudes = cursor.fetchall()

    # Obtener convocatorias
    cursor.execute("SELECT id, nombre, descripcion, fecha_inicio, fecha_fin FROM convocatorias")
    convocatorias = cursor.fetchall()

    # Obtener requisitos
    cursor.execute("SELECT * FROM requisitos")
    requisitos = cursor.fetchall()

    # obtener documentos
    cursor.execute("SELECT * FROM documentos")
    documentos = cursor.fetchall()

    #Obtener solicitudes de pago
    cursor.execute("SELECT * FROM pago ORDER BY id DESC")
    pagos = cursor.fetchall()


    conexion.close()

    now = datetime.now().strftime('%Y-%m-%d')
    return render_template('admin_panel.html', solicitudes=solicitudes, convocatorias=convocatorias, requisitos=requisitos, documentos=documentos, pagos=pagos, now=now)

# Eliminar solicitud
@admin_bp.route('/eliminar_solicitud/<int:id>', methods=['POST'])
def eliminar_solicitud(id):
    """Permite al administrador eliminar una solicitud por su ID."""
    if not session.get('admin_id'):
        flash("Debes iniciar sesión para acceder al panel.")
        return redirect(url_for('admin.login'))

    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM solicitudes WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()

    flash("Solicitud eliminada correctamente ")
    return redirect(url_for('admin.panel'))


# Actualizar estatus
@admin_bp.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    if not session.get('admin_id'):
        flash("Acceso no autorizado.")
        return redirect(url_for('admin.login'))

    nuevo_estatus = request.form('estatus')
    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()
    cursor.execute("UPDATE solicitudes SET estatus = ? WHERE id = ?", (nuevo_estatus, id))
    conexion.commit()
    conexion.close()
    flash(" Estatus actualizado correctamente.")
    return redirect(url_for('admin.panel'))

# Exportar a Excel
@admin_bp.route('/descargar_excel')
def descargar_excel():
    if not session.get('admin_id'):
        flash("Acceso no autorizado.")
        return redirect(url_for('admin.login'))

    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM solicitudes ORDER BY id DESC")
    solicitudes = cursor.fetchall()
    conexion.close()

    # Crear archivo Excel en memoria
    wb = Workbook()
    ws = wb.active
    ws.title = "Solicitudes de Becas"

    # Encabezados
    encabezados = [
        "ID", "Matricula", "Nombre", "Apellidos","curp","nss", "carrera", "beca", "porcentaje cursado", "materias reprobadas", "promedio", "Telefono", "Correo", "Actividades", "Horario", "Area", "Coordinador", "PDF", "Fecha Registro", "Estatus", "Comentario Admin"
    ]
    ws.append(encabezados)

    # Agregar filas
    for s in solicitudes:
        ws.append(s)

    # Guardar en memoria (sin archivo temporal)
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # Enviar archivo al navegador
    return send_file(
        output,
        as_attachment=True,
        download_name="solicitudes_becas.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@admin_bp.route('/excel_pagos')
def excel_pagos():
    if not session.get('admin_id'):
        flash("Acceso no autorizado.")
        return redirect(url_for('admin.login'))

    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM pago ORDER BY id DESC")
    solicitudes = cursor.fetchall()
    conexion.close()

    # Crear archivo Excel en memoria
    wb = Workbook()
    ws = wb.active
    ws.title = "Formulario de Pagos"

    # Encabezados
    encabezados = [
        "ID", "Nombre", "Apellidos", "Matricula", "Archivo Pago", "Estatus", "Comentario Admin"
    ]
    ws.append(encabezados)

    # Agregar filas
    for s in solicitudes:
        ws.append(s)

    # Guardar en memoria (sin archivo temporal)
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # Enviar archivo al navegador
    return send_file(
        output,
        as_attachment=True,
        download_name="Formulario_pagos.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


#panel de pagos
@admin_bp.route('/pagos', methods=['GET', 'POST'])
def pagos_admin():
    if not session.get('admin_id'):
        flash("Debes iniciar sesión para acceder al panel de pagos.")
        return redirect(url_for('admin.login'))

    conexion = sqlite3.connect(DB)
    cursor = conexion.cursor()

    # Si el admin actualiza un pago (estatus o comentario)
    if request.method == 'POST':
        id_pago = request.form.get('id_pago')
        nuevo_estatus = request.form.get('estatus')
        comentario = request.form.get('comentario')

        if id_pago and nuevo_estatus:
            cursor.execute('''
                UPDATE pago
                SET estatus = ?, comentario_admin = ?
                WHERE id = ?
            ''', (nuevo_estatus, comentario, id_pago))
            conexion.commit()
            flash('Pago actualizado correctamente')
        else:
            flash('Error: faltan datos para actualizar el pago.')

    # Obtener todos los pagos
    cursor.execute('SELECT id, nombre, apellidos, matricula, archivo_pago, estatus, comentario_admin FROM pago ORDER BY id DESC')
    pagos = cursor.fetchall()
    conexion.close()

    return render_template('admin_pagos.html', pagos=pagos)

# Eliminar pago
@admin_bp.route('/eliminar_pago/<int:id>', methods=['POST'])
def eliminar_pago(id):
    """Permite al administrador eliminar un pago por su ID y borrar el PDF asociado."""
    if not session.get('admin_id'):
        flash("Debes iniciar sesión para acceder al panel.")
        return redirect(url_for('admin.login'))

    # 1. Obtener el nombre del archivo para borrarlo después
    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT archivo_pago FROM pago WHERE id = ?", (id,))
    resultado = cursor.fetchone()

    if resultado:
        archivo_pdf = resultado[0]  # nombre del archivo
    else:
        archivo_pdf = None

    # 2. Eliminar el registro de la base de datos
    cursor.execute("DELETE FROM pago WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()

    # 3. Borrar el archivo físico si existe
    if archivo_pdf:
        ruta_archivo = os.path.join('static', 'uploads', 'pagos', archivo_pdf)
        if os.path.exists(ruta_archivo):
            try:
                os.remove(ruta_archivo)
            except Exception as e:
                print("Error al eliminar archivo:", e)

    flash("Pago eliminado correctamente.")
    return redirect(url_for('admin.panel'))


@admin_bp.route('/actualizar_admin', methods=['POST'])
def actualizar_admin():
    if not session.get('admin_id'):
        flash("Debes iniciar sesión.")
        return redirect(url_for('admin.login'))

    nuevo_username = request.form.get('nuevo_username')
    password_actual = request.form.get('password_actual')
    nueva_password = request.form.get('nueva_password')
    confirmar_password = request.form.get('confirmar_password')

    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()

    # Obtener datos actuales del admin
    cursor.execute("SELECT id, username, password_hash FROM admin WHERE id = ?", (session['admin_id'],))
    admin = cursor.fetchone()

    if not admin:
        flash("Administrador no encontrado.")
        conexion.close()
        return redirect(url_for('admin.panel'))

    admin_id = admin[0]
    password_hash_db = admin[2]

    # Verificar contraseña actual
    if not check_password_hash(password_hash_db, password_actual):
        flash("La contraseña actual es incorrecta ❌")
        conexion.close()
        return redirect(url_for('admin.panel'))

    # Si quiere cambiar contraseña
    if nueva_password:
        if nueva_password != confirmar_password:
            flash("Las nuevas contraseñas no coinciden ❌")
            conexion.close()
            return redirect(url_for('admin.panel'))

        nueva_password_hash = generate_password_hash(nueva_password)

        cursor.execute("""
            UPDATE admin
            SET username = ?, password_hash = ?
            WHERE id = ?
        """, (nuevo_username, nueva_password_hash, admin_id))

    else:
        cursor.execute("""
            UPDATE admin
            SET username = ?
            WHERE id = ?
        """, (nuevo_username, admin_id))

    conexion.commit()
    conexion.close()

    # Actualizar sesión
    session['admin_username'] = nuevo_username

    flash("Datos actualizados correctamente ✅")
    return redirect(url_for('admin.panel'))
