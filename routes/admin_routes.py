from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3

admin_bp = Blueprint('admin', __name__)

# Página del panel principal
@admin_bp.route('/panel')
def panel():
    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM solicitudes ORDER BY fecha_registro DESC")
    solicitudes = cursor.fetchall()
    conexion.close()
    return render_template('admin_panel.html', solicitudes=solicitudes)

# Ruta para actualizar estatus
@admin_bp.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    nuevo_estatus = request.form['estatus']
    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()
    cursor.execute("UPDATE solicitudes SET estatus = ? WHERE id = ?", (nuevo_estatus, id))
    conexion.commit()
    conexion.close()
    flash("✅ Estatus actualizado correctamente.")
    return redirect(url_for('admin.panel'))
