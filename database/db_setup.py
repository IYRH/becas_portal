import sqlite3

def crear_base_datos():
    conexion = sqlite3.connect('becas.db')
    cursor = conexion.cursor()

    # Tabla de solicitudes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solicitudes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT NOT NULL,                   
            nombre TEXT NOT NULL,                               
            apellidos TEXT NOT NULL,
            curp TEXT NOT NULL,
            nss TEXT,  
            carrera TEXT, 
            beca TEXT,
            porcentaje_cursado INTEGER,
            materias_reprobadas INTEGER,                                                     
            promedio REAL,
            telefono TEXT NOT NULL,                                                                     
            correo TEXT NOT NULL,                                                                       
            actividades TEXT, 
            horario TEXT,
            area TEXT,
            coordinador TEXT,                                                                                                                                                
            pdf TEXT,
            fecha_registro TEXT DEFAULT (datetime('now','localtime')),                                           
            estatus TEXT DEFAULT 'Recibida',                    
            comentario_admin TEXT                             
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

    # Tabla de formulario de pago
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pago (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL ,
            apellidos TEXT NOT NULL,
            matricula TEXT NOT NULL,
            archivo_pago TEXT,
            estatus TEXT DEFAULT 'Recibida',                    
            comentario_admin TEXT  
        )
    ''')

    # Tabla de requisitos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requisitos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contenido TEXT NOT NULL
        )
    ''')

    # Tabla de documentos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descripcion TEXT NOT NULL
    )
''')

    # Verifica si ya hay un registro inicial
    #cursor.execute("SELECT COUNT(*) FROM requisitos")
    #if cursor.fetchone()[0] == 0:
    #    cursor.execute("INSERT INTO requisitos (descripcion) VALUES (?)", 
    #                   ("Aquí aparecerán los requisitos para solicitar una beca.",))



    conexion.commit()
    conexion.close()
    print(" Base de datos creada correctamente.")

    def get_db_connection():
        conn = sqlite3.connect('becas.db')
        conn.row_factory = sqlite3.Row
    return conn
