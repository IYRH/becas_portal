from flask import Flask, render_template, request
from database.db_setup import crear_base_datos
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # muestra tu portal de becas

if __name__ == '__main__':
    crear_base_datos()
    app.run(debug=True)
