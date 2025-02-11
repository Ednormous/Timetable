from flask import Blueprint

tutor = Blueprint('tutor', __name__)

from app.tutor import routes
