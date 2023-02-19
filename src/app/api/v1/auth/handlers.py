from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, request
from flask_jwt_extended import current_user, get_jti, get_jwt, jwt_required
from pydantic import IPvAnyNetwork

from app.api.v1.auth.schemas import (
    ChangePasswordUserRequest,
    LoginHistoryData,
    LoginUserRequest,
    LoginUserResData,
    LogoutUser,
    RegUserRequest,
    RoleData,
)
from app.db import db, models
from settings import logger

from ..schemas import BaseResponse
from ..utils import get_body
from .utils import create_access_and_refresh_jwt, invalidate_jwt

router = Blueprint("auth", __name__)


@router.route("/registration", methods=["POST"])
def registration():
    """
    User registration.
    No auth header needed.
    """
    body: RegUserRequest = get_body(RegUserRequest)
    login_in_db = models.User.query.filter_by(login=body.login).one_or_none()
    if login_in_db:
        error_message = "Login already exists"
        return (
            BaseResponse(success=False, error=error_message).dict()
        ), HTTPStatus.BAD_REQUEST

    user = models.User(**body.dict())
    db.session.add(user)
    db.session.commit()

    return BaseResponse(success=True, error="").dict(), HTTPStatus.OK


@router.route("/password_change", methods=["POST"])
@jwt_required()
def password_change():
    """
    User password change.
    """
    body: ChangePasswordUserRequest = get_body(ChangePasswordUserRequest)

    if current_user.verify_password(body.old_password):
        current_user.password = body.new_password

        # Old tokens invalidation
        for token in models.JWTStore.query.filter_by(
            user_id=current_user.id
        ).all():
            invalidate_jwt(token.jwt_id, token.type)
            db.session.delete(token)
        db.session.commit()
    else:
        error_message = "Wrong password"
        return (
            BaseResponse(success=False, error=error_message).dict()
        ), HTTPStatus.UNAUTHORIZED

    jwt_tokens = create_access_and_refresh_jwt(current_user)
    return (
        BaseResponse(data=jwt_tokens).dict(),
        HTTPStatus.OK,
    )


@router.route("/login", methods=["POST"])
def login():
    """
    User login.
    """
    body: LoginUserRequest = get_body(LoginUserRequest)

    user = models.User.query.filter_by(login=body.login).one_or_none()
    if not user or not user.verify_password(body.password):
        return (
            BaseResponse(
                success=False, error="Wrong username or password"
            ).dict(),
            HTTPStatus.UNAUTHORIZED,
        )

    db.session.add(
        models.LoginHistory(
            user_id=user.id,
            ip=request.environ.get("HTTP_X_REAL_IP", request.remote_addr),
            user_agent=request.headers.get("User-Agent"),
            datetime=datetime.now(),
        )
    )
    db.session.commit()
    jwt_tokens = create_access_and_refresh_jwt(user)
    return (
        BaseResponse(data=jwt_tokens).dict(),
        HTTPStatus.OK,
    )


@router.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    User logout.
    To logout client must make two requests, one for each JWT type.
    """
    body: LogoutUser = get_body(LogoutUser)

    current_tokens = [get_jwt()["jti"], get_jti(body.refresh_token)]

    for token in models.JWTStore.query.filter_by(
        user_id=current_user.id
    ).all():
        if token.jwt_id in current_tokens:
            invalidate_jwt(token.jwt_id, token.type)
            db.session.delete(token)
    db.session.commit()

    return BaseResponse(success=True, error="").dict(), HTTPStatus.OK


@router.route("/logout_all", methods=["POST"])
@jwt_required()
def logout_all():
    """
    User logout all other sessions.
    """
    body: LogoutUser = get_body(LogoutUser)

    current_tokens = [get_jwt()["jti"], get_jti(body.refresh_token)]
    for token in models.JWTStore.query.filter_by(
        user_id=current_user.id
    ).all():
        if token.jwt_id not in current_tokens:
            invalidate_jwt(token.jwt_id, token.type)
            db.session.delete(token)
    db.session.commit()
    return BaseResponse(success=True, error="").dict(), HTTPStatus.OK


@router.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)  # Only allow refresh tokens to access this route.
def refresh():
    """
    Takes refresh JWT token as input, issues a new access and refresh token pair.
    """
    old_refresh_token_jti = get_jwt()["jti"]
    old_refresh_token = models.JWTStore.query.filter_by(
        user_id=current_user.id, jwt_id=old_refresh_token_jti
    ).one_or_none()
    if old_refresh_token:
        db.session.delete(old_refresh_token)
        db.session.commit()
    invalidate_jwt(old_refresh_token_jti, "refresh")

    jwt_tokens = create_access_and_refresh_jwt(current_user)

    return (
        BaseResponse(data=jwt_tokens).dict(),
        HTTPStatus.OK,
    )


@router.route("/user/login_history", methods=["GET"])
@jwt_required()
def user_login_history():
    """
    User login history.
    """
    data: list[LoginHistoryData] = []
    for row in models.LoginHistory.query.filter_by(
        user_id=current_user.id
    ).all():
        data.append(
            LoginHistoryData(
                ip=row.ip, user_agent=row.user_agent, datetime=row.datetime
            )
        )
    return BaseResponse(data=data).dict(), HTTPStatus.OK


@router.route("/user/roles", methods=["GET"])
@jwt_required()
def user_roles_list():
    """
    User roles list.
    """
    data: list[RoleData] = []
    for role in current_user.roles:
        data.append(RoleData(id=role.id, name=role.name))

    return BaseResponse(data=data).dict(), HTTPStatus.OK
