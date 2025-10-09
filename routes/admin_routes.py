from flask import Blueprint, render_template

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login')
def login():
    return render_template('admin_login.html')

@admin_bp.route('/panel')
def panel():
    return render_template('admin_panel.html')
