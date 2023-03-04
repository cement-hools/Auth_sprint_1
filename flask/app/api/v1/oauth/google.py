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
    # oauth = app.oauth
    # oauth.yandex.authorize_access_token()
    # url = "https://login.yandex.ru/info"
    # response = oauth.yandex.get(url)
    # account_user = User(**response.json())
    # data = login_yandex_user(account_user)
    # return BaseResponse(data=data).dict(), HTTPStatus.OK

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
    # oauth = current_app.extensions["authlib.integrations.flask_client"]
    # url = url_for("v1.oauth.yandex.callback", _external=True)
    # return oauth.yandex.authorize_redirect(url)
    redirect_uri = url_for("v1.oauth.google.callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)
