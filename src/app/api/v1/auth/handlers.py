from http import HTTPStatus

from flask import Blueprint, request
from flask_jwt_extended import current_user, get_jti, get_jwt, jwt_required

from app.api.v1.auth.schemas import (
    ChangePasswordUserRequest,
    LoginHistoryData,
    LoginUserRequest,
    LogoutUser,
    RegUserRequest,
    RoleData,
    UserData,
)
from app.services import auth

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
    result = auth.registration(
        login=body.login,
        email=body.email,
        password=body.password,
    )
    if result.error_message:
        return (
            BaseResponse(success=False, error=result.error_message).dict()
        ), HTTPStatus.BAD_REQUEST
    else:
        return BaseResponse(success=True, error="").dict(), HTTPStatus.OK


@router.route("/login", methods=["POST"])
def login():
    """
    User login.
    """
    body: LoginUserRequest = get_body(LoginUserRequest)

    result = auth.login(
        login=body.login,
        password=body.password,
    )

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


@router.route("/password_change", methods=["POST"])
@jwt_required()
def password_change():
    """
    User password change.
    """
    body: ChangePasswordUserRequest = get_body(ChangePasswordUserRequest)
    result = auth.password_change(
        user=current_user,
        old_password=body.old_password,
        new_password=body.new_password,
    )
    if result.error_message:
        return (
            BaseResponse(success=False, error=result.error_message).dict()
        ), HTTPStatus.UNAUTHORIZED
    else:
        return (
            BaseResponse(data=result.data).dict(),
            HTTPStatus.OK,
        )


@router.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    User logout.
    """
    body: LogoutUser = get_body(LogoutUser)

    current_tokens = [get_jwt()["jti"], get_jti(body.refresh_token)]

    result = auth.logout(current_user, current_tokens)

    return BaseResponse(success=result.success).dict(), HTTPStatus.OK


@router.route("/logout_all", methods=["POST"])
@jwt_required()
def logout_all_other():
    """
    User logout all other sessions.
    """
    body: LogoutUser = get_body(LogoutUser)

    current_tokens = [get_jwt()["jti"], get_jti(body.refresh_token)]
    result = auth.logout_other_tokens(current_user, current_tokens)
    return BaseResponse(success=result.success).dict(), HTTPStatus.OK


@router.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)  # Only allow refresh tokens to access this route.
def refresh_token():
    """
    Takes refresh JWT token as input, issues a new access and refresh token pair.
    """
    old_refresh_token_jti = get_jwt()["jti"]
    result = auth.refresh_token(current_user, old_refresh_token_jti)

    return (
        BaseResponse(success=result.success, data=result.data).dict(),
        HTTPStatus.OK,
    )


@router.route("/user/login_history", methods=["GET"])
@jwt_required()
def login_history():
    """
    User login history.
    """
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    result = auth.login_history_w_pagination(
        user=current_user,
        page=page,
        per_page=per_page,
    )
    return (
        BaseResponse(
            success=result.success, data=LoginHistoryData(**result.data)
        ).dict(),
        HTTPStatus.OK,
    )


@router.route("/user/roles", methods=["GET"])
@jwt_required()
def user_roles_list():
    """
    User roles list.
    """
    result = auth.roles_list(current_user)
    data: list[RoleData] = []
    for role in result.data:
        data.append(RoleData(**role))
    return (
        BaseResponse(success=result.success, data=data).dict(),
        HTTPStatus.OK,
    )
