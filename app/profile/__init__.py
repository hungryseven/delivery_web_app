from flask import Blueprint

bp = Blueprint('prifile', __name__)

from app.profile import views