from http import HTTPStatus

from flask import Blueprint
from werkzeug.exceptions import HTTPException

from app.api.v1 import auth, roles, oauth
from app.jwt_app import jwt

from .schemas import BaseResponse

bp = Blueprint("v1", __name__, url_prefix="/api/v1")

bp.register_blueprint(auth.router)
bp.register_blueprint(roles.router)
bp.register_blueprint(oauth.router)


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
    return response, HTTPStatus.INTERNAL_SERVER_ERROR


@bp.errorhandler(404)
def item_not_found(e):
    """Return JSON instead of HTML for 404 errors."""
    response = e.get_response()
    data = BaseResponse(success=False, error=e.description)
    response.data = data.json()
    response.content_type = "application/json"
    return response, HTTPStatus.NOT_FOUND


@bp.errorhandler(422)
def unprocessable_entity(e):
    """Return JSON instead of HTML for 422 errors."""
    response = e.get_response()
    data = BaseResponse(success=False, error=e.description)
    response.data = data.json()
    response.content_type = "application/json"
    return response, HTTPStatus.UNPROCESSABLE_ENTITY


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return (
        BaseResponse(success=False, error="Expired token").dict(),
        HTTPStatus.UNAUTHORIZED,
    )


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        BaseResponse(success=False, error=error).dict(),
        HTTPStatus.UNAUTHORIZED,
    )
