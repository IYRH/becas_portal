import sqlite3

conexion = sqlite3.connect('becas.db')
cursor = conexion.cursor()

cursor.execute("ALTER TABLE solicitudes ADD COLUMN comentario_admin TEXT;")

conexion.commit()
conexion.close()

print(" Columna 'comentario_admin' agregada correctamente.")
