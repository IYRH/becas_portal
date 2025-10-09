from flask import Flask, render_template, request
from database.db_setup import crear_base_datos
from routes.main_routes import main_bp
from routes.admin_routes import admin_bp


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # muestra tu portal de becas

if __name__ == '__main__':
    crear_base_datos()
    app.run(debug=True)
