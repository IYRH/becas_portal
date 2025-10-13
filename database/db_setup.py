import sqlite3

def crear_base_datos():
    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()

    # Tabla de solicitudes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solicitudes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            matricula TEXT NOT NULL,
            curp TEXT NOT NULL,
            correo TEXT NOT NULL,
            telefono TEXT,
            nss TEXT,
            porcentaje_cursado INTEGER,
            carrera TEXT,
            beca TEXT,
            pdf TEXT,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            estatus TEXT DEFAULT 'Recibida'
        )
    ''')

    # Tabla de administradores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            contraseña_hash TEXT NOT NULL
        )
    ''')

    # Tabla de convocatorias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS convocatorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            descripcion TEXT,
            fecha_inicio TEXT,
            fecha_fin TEXT,
            activa INTEGER DEFAULT 0
        )
    ''')


    conexion.commit()
    conexion.close()
    print(" Base de datos creada correctamente.")
