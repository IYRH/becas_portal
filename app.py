from flask import Flask
from database.db_setup import crear_base_datos
from routes.main_routes import main_bp
from routes.admin_routes import admin_bp
import os

app = Flask(__name__)
app.secret_key = "clave-secreta-segura"  # Necesaria para sesiones Flask

# Registrar los blueprints (rutas)
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp, url_prefix="/admin")

# Crear la base de datos si no existe
if not os.path.exists("becas.db"):
    crear_base_datos()
    print("Base de datos creada exitosamente.")
else:
    print("La base de datos ya existe. No se volverá a crear.")

if __name__ == "__main__":
    app.run(debug=True)
