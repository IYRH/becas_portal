from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
import sqlite3
from openpyxl import Workbook
import io

admin_bp = Blueprint('admin', __name__)

# Credenciales del administrador (puedes cambiarlas)
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
@admin_bp.route('/panel')
def panel():
    if not session.get('admin'):
        flash("Debes iniciar sesión para acceder al panel.")
        return redirect(url_for('admin.login'))

    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM solicitudes ORDER BY fecha_registro DESC")
    solicitudes = cursor.fetchall()
    conexion.close()
    return render_template('admin_panel.html', solicitudes=solicitudes)

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
        "ID", "Nombre","Apellidos","Matricula","Correo", "Teléfono", "NSS",
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