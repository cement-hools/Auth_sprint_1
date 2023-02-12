from app.models.requests import (
    BaseResponse,
    ChangePasswordUserRequest,
    HistoryResponse,
    LoginUserRequest,
    LoginUserResponse,
    LogoutAllUser,
    LogoutUser,
    RefreshToken,
    RefreshTokenResponse,
    RegUserRequest,
    RegUserResponse,
    UsersRoleResponse,
)
from flask import Blueprint, request
from flask_pydantic import validate

router = Blueprint("auth", __name__)


@router.route("/registration", methods=["POST"])
@validate()
def registration(body: RegUserRequest):
    """
    User registration.
    No auth header needed.
    """
    data = request.get_json()
    print(data)
    # TODO: logic

    return RegUserResponse(success=True, data=data)


@router.route("/password/change", methods=["POST"])
@validate()
def password_change(body: ChangePasswordUserRequest):
    """
    User password change.
    """
    data = request.get_json()
    print(data)
    # TODO: logic

    return BaseResponse(success=True, error="")


@router.route("/login", methods=["POST"])
@validate()
def login(body: LoginUserRequest):
    """
    User login.
    """
    data = request.get_json()
    print(data)
    # TODO: logic
    return LoginUserResponse(success=True, error="", data=data)


@router.route("/logout", methods=["POST"])
@validate()
def logout(body: LogoutUser):
    """
    User logout.
    """
    data = request.get_json()
    print(data)
    # TODO: logic
    return BaseResponse(success=True, error="")


@router.route("/logout_all", methods=["POST"])
@validate()
def logout_all(body: LogoutAllUser):
    """
    User logout all other sessions.
    """
    data = request.get_json()
    print(data)
    # TODO: logic
    return BaseResponse(success=True, error="")


@router.route("/refresh", methods=["POST"])
@validate()
def refresh(body: RefreshToken):
    """
    Refresh token.
    """
    data = request.get_json()
    print(data)
    # TODO: logic
    return RefreshTokenResponse(success=True, error="", data=data)


@router.route("/user/<string:user_id>/history", methods=["GET"])
@validate()
def user_login_history():
    """
    User login history.
    """
    data = request.get_json()
    print(data)
    # TODO: logic
    return HistoryResponse(success=True, error="", data=data)


@router.route("/user/<string:user_id>/roles", methods=["GET"])
@validate()
def user_roles_list():
    """
    User roles list..
    """
    data = request.get_json()
    print(data)
    # TODO: logic
    return UsersRoleResponse(success=True, error="", data=data)
