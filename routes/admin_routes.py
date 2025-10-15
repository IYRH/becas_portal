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
            comentario = request.form.get('comentario')

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
            convocatoria_id = request.form.get['id']
            fecha_inicio = request.form.get['fecha_inicio']
            fecha_fin = request.form.get['fecha_fin']

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

    # --- Obtener datos actualizados ---
    cursor.execute("SELECT id, nombre, apellidos,matricula , correo, telefono, nss, carrera, estatus, comentario_admin, fecha_registro FROM solicitudes ORDER BY fecha_registro DESC")
    solicitudes = cursor.fetchall()

    cursor.execute("SELECT id, nombre, descripcion, fecha_inicio, fecha_fin FROM convocatorias")
    convocatorias = cursor.fetchall()

    conexion.close()

    now = datetime.now().strftime('%Y-%m-%d')
    return render_template('admin_panel.html', solicitudes=solicitudes, convocatorias=convocatorias, now=now)




# Actualizar estatus
@admin_bp.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    if not session.get('admin'):
        flash("Acceso no autorizado.")
        return redirect(url_for('admin.login'))

    nuevo_estatus = request.form['estatus']
    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()
    cursor.execute("UPDATE solicitudes SET estatus = ? WHERE id = ?", (nuevo_estatus, id))
    conexion.commit()
    conexion.close()
    flash("✅ Estatus actualizado correctamente.")
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

