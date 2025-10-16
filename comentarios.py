import sqlite3
conexion = sqlite3.connect('becas.db')
cursor = conexion.cursor()
cursor.execute("PRAGMA table_info(solicitudes)")
for col in cursor.fetchall():
    print(col)
conexion.close()
