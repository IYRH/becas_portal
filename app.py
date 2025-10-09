from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # muestra tu portal de becas

if __name__ == '__main__':
    app.run(debug=True)
