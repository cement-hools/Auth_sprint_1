from flask import Blueprint

from app.api.v1 import auth, roles

bp = Blueprint("v1", __name__, url_prefix="/api/v1")

bp.register_blueprint(auth.router)
bp.register_blueprint(roles.router)
