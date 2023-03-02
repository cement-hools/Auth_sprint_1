from http import HTTPStatus

from flask import Blueprint, current_app, request, url_for

import app
from app.services.oauth import login_yandex_user

from ..schemas import BaseResponse
from .schemas.yandex import User

router = Blueprint("yandex", __name__, url_prefix="/yandex")


@router.route("/callback", methods=["GET"])
def callback():
    """."""
    oauth = app.oauth
    oauth.yandex.authorize_access_token()
    url = "https://login.yandex.ru/info"
    response = oauth.yandex.get(url)
    account_user = User(**response.json())
    data = login_yandex_user(account_user)
    return BaseResponse(data=data).dict(), HTTPStatus.OK


@router.route("/login", methods=["GET"])
def login():
    oauth = current_app.extensions["authlib.integrations.flask_client"]
    url = url_for("v1.oauth.yandex.callback", _external=True)
    return oauth.yandex.authorize_redirect(url)
