# app/tutor/routes.py
from functools import wraps
from flask import render_template, abort
from flask_login import login_required, current_user
from app.tutor import tutor

def roles_required(role):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if current_user.role != role:
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator

@tutor.route('/', methods=['GET'])
@login_required
@roles_required('tutor')
def dashboard():
    return "<h1>Tutor Dashboard</h1><p>View your scheduled sessions here.</p>"
