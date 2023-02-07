from app.api.v1 import auth
from flask import Blueprint

bp = Blueprint('v1', __name__, url_prefix='/api/v1')

bp.register_blueprint(auth.router)
