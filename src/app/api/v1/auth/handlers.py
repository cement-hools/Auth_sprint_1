from datetime import datetime
from http import HTTPStatus

from app.api.v1.auth.schemas import (
    ChangePasswordUserRequest,
    HistoryData,
    LoginUserRequest,
    LoginUserResData,
    LogoutAllUser,
    LogoutUser,
    RefreshToken,
    RefreshTokenData,
    RegUserRequest,
    RegUserResponse,
    RoleData,
)
from app.db import db, models
from flask import Blueprint, request
from flask_dantic import serialize
from settings import logger

from ..schemas import BaseResponse
from ..utils import get_body

router = Blueprint("auth", __name__)


@router.route("/registration", methods=["POST"])
def registration():
    """
    User registration.
    No auth header needed.
    """
    body: RegUserRequest = get_body(RegUserRequest)
    print(body)
    # TODO: logic

    return RegUserResponse(success=True, data=body).json(), HTTPStatus.OK


@router.route("/password/change", methods=["POST"])
def password_change():
    """
    User password change.
    """

    body: ChangePasswordUserRequest = get_body(ChangePasswordUserRequest)
    print(body)
    # TODO: logic

    return BaseResponse(success=True, error="").json(), HTTPStatus.OK


@router.route("/login", methods=["POST"])
def login():
    """
    User login.
    """
    body: LoginUserRequest = get_body(LoginUserRequest)
    print(body)

    # TODO: logic
    return (
        BaseResponse(
            data=LoginUserResData(login="", token="", datetime=datetime.today())
        ).json(),
        HTTPStatus.OK,
    )


@router.route("/logout", methods=["POST"])
def logout():
    """
    User logout.
    """

    body: LogoutUser = get_body(LogoutUser)
    print(body)
    # TODO: logic
    return BaseResponse(success=True, error="").json(), HTTPStatus.OK


@router.route("/logout_all", methods=["POST"])
def logout_all():
    """
    User logout all other sessions.
    """
    body: LogoutAllUser = get_body(LogoutAllUser)
    print(body)
    # TODO: logic
    return BaseResponse(success=True, error="").json(), HTTPStatus.OK


@router.route("/refresh", methods=["POST"])
def refresh():
    """
    Refresh token.
    """
    body: RefreshToken = get_body(RefreshToken)
    print(body)
    # TODO: logic
    return (
        BaseResponse(
            data=RefreshTokenData(refresh_token="", access_token=""),
        ).json(),
        HTTPStatus.OK,
    )


@router.route("/user/<string:user_id>/history", methods=["GET"])
def user_login_history():
    """
    User login history.
    """
    data: list[HistoryData] = request.get_json()
    print(data)
    # TODO: logic
    return BaseResponse(data=data).json(), HTTPStatus.OK


@router.route("/user/<string:user_id>/roles", methods=["GET"])
def user_roles_list():
    """
    User roles list..
    """
    data: list[RoleData] = request.get_json()
    print(data)
    # TODO: logic
    return BaseResponse(data=data).json(), HTTPStatus.OK
