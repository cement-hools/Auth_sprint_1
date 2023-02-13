import json
from http import HTTPStatus

import werkzeug
from app.api.v1 import auth, roles
from flask import Blueprint
from werkzeug.exceptions import HTTPException

from .schemas import BaseResponse

bp = Blueprint("v1", __name__, url_prefix="/api/v1")

bp.register_blueprint(auth.router)
bp.register_blueprint(roles.router)


@bp.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    error_data = {
        "code": e.code,
        "name": e.name,
        "description": e.description,
    }
    data = BaseResponse(success=False, error=error_data)
    response.data = data.json()
    response.content_type = "application/json"
    return response


@bp.errorhandler(404)
def page_not_found(e):
    """Return JSON instead of HTML for 404 errors."""
    response = e.get_response()
    data = BaseResponse(success=False, error=e.description)
    response.data = data.json()
    response.content_type = "application/json"
    return response, HTTPStatus.NOT_FOUND
