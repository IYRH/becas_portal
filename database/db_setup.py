import sqlite3

def crear_base_datos():
    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()

    # Tabla de solicitudes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solicitudes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,               <!-- s[0] -->
            nombre TEXT NOT NULL,                               <!-- s[1] -->
            apellidos TEXT NOT NULL,                            <!-- s[2] --> 
            matricula TEXT NOT NULL,                            <!-- s[3] -->
            promedio REAL,                                      <!-- s[4] -->
            curp TEXT NOT NULL,                                 <!-- s[5] -->
            correo TEXT NOT NULL,                               <!-- s[6] -->
            telefono TEXT,                                      <!-- s[7] -->
            nss TEXT,                                           <!-- s[8] -->
            porcentaje_cursado INTEGER,                         <!-- s[9] -->
            carrera TEXT,                                       <!-- s[10] -->
            beca TEXT,                                          <!-- s[11] -->
            pdf TEXT,                                           <!-- s[12] -->
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,  <!-- s[13] -->
            estatus TEXT DEFAULT 'Recibida',                    <!-- s[14] -->
            comentario_admin TEXT                               <!-- s[15] -->
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
