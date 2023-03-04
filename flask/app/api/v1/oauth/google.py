from http import HTTPStatus

from flask import Blueprint, current_app, request, url_for

from app import oauth
from app.services.oauth import login_google_user

from ..schemas import BaseResponse
from .schemas.google import Token

router = Blueprint("google", __name__, url_prefix="/google")


@router.route("/callback", methods=["GET"])
def callback():
    """Google OAuth callback"""
    token = oauth.google.authorize_access_token()

    result = login_google_user(Token(**token["userinfo"]))

    if result.error_message:
        return (
            BaseResponse(
                success=False, error="Wrong username or password"
            ).dict(),
            HTTPStatus.UNAUTHORIZED,
        )
    else:
        return (
            BaseResponse(data=result.data).dict(),
            HTTPStatus.OK,
        )


@router.route("/login", methods=["GET"])
def login():
    redirect_uri = url_for("v1.oauth.google.callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)
