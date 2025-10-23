from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
import sqlite3
from datetime import datetime
from openpyxl import Workbook
import io

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
DB = 'becas.db'

# Credenciales del administrador
ADMIN_USER = "admin"
ADMIN_PASS = "12345"

# Página de login
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        if usuario == ADMIN_USER and password == ADMIN_PASS:
            session['admin'] = True
            flash("Bienvenido, administrador.")
            return redirect(url_for('admin.panel'))
        else:
            flash("Usuario o contraseña incorrectos.")
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
    if not session.get('admin'):
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


    conexion.close()

    now = datetime.now().strftime('%Y-%m-%d')
    return render_template('admin_panel.html', solicitudes=solicitudes, convocatorias=convocatorias, requisitos=requisitos, documentos=documentos, now=now)

# Eliminar solicitud
@admin_bp.route('/eliminar_solicitud/<int:id>', methods=['POST'])
def eliminar_solicitud(id):
    """Permite al administrador eliminar una solicitud por su ID."""
    if not session.get('admin'):
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
    if not session.get('admin'):
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
    if not session.get('admin'):
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
        "ID", "Nombre","Apellidos","Matricula","Promedio","Correo", "Teléfono", "NSS",
        "% Materias Cursadas", "Carrera", "Estatus", "Fecha Registro"
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







