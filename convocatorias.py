import sqlite3

conexion = sqlite3.connect('becas.db')
cursor = conexion.cursor()

convocatorias = [
    ("Beca de Servicio Social", "Al realizar tu Servicio Social tiene la opcion de postularte para una beca.", "2025-09-01", "2025-12-31", 1),
    ("Beca de Practicas Profesionales", "Puedes acceder a una beca al realizar tus Practicas Profesionales.", "2025-10-01", "2025-10-30", 1),
    ("Beca de Monitores", "Apoyo para concluir tu Licenciatura.", "2025-07-01", "2025-08-31", 0)
]

cursor.executemany(
    "INSERT OR IGNORE INTO convocatorias (nombre, descripcion, fecha_inicio, fecha_fin, activa) VALUES (?, ?, ?, ?, ?)",
    convocatorias
)
conexion.commit()
conexion.close()

print("¡¡¡ Convocatorias iniciales con fechas agregadas correctamente !!!")
