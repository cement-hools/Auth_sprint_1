from datetime import datetime

from flask import request

from app.db import db
from app.db.models.jwt import JWTStore
from app.db.models.user import LoginHistory, User

from .auth_utils import create_access_and_refresh_jwt, invalidate_jwt
from .schemas import ServiceResult


def registration(
    login: str,
    email: str,
    password: str,
) -> ServiceResult:
    login_in_db = User.query.filter(
        (User.login == login) | (User.email == email)
    ).first()
    if login_in_db:
        error_message = "Login or email already exists"
        return ServiceResult(success=False, error_message=error_message)

    user = User(
        login=login,
        email=email,
        password=password,
    )
    db.session.add(user)
    db.session.commit()

    return ServiceResult(success=True, data=user)


def login(
    login: str, password: str, is_social_auth: bool = False
) -> ServiceResult:
    user = User.query.filter_by(login=login).one_or_none()

    if user:
        if user.verify_password(password) or is_social_auth:
            db.session.add(
                LoginHistory(
                    user_id=user.id,
                    ip=request.environ.get(
                        "HTTP_X_REAL_IP", request.remote_addr
                    ),
                    user_agent=request.headers.get("User-Agent"),
                    datetime=datetime.now(),
                )
            )
            db.session.commit()
            jwt_tokens = create_access_and_refresh_jwt(user)
            return ServiceResult(success=True, data=jwt_tokens)

    error_message = "Wrong login or password"
    return ServiceResult(success=False, error_message=error_message)


def password_change(
    user: User,
    old_password: str,
    new_password: str,
) -> ServiceResult:
    if user.verify_password(old_password):
        user.password = new_password
    else:
        error_message = "Wrong password"
        return ServiceResult(success=False, error_message=error_message)

    # Old tokens invalidation
    for token in JWTStore.query.filter_by(user_id=user.id).all():
        invalidate_jwt(token.jwt_id, token.type)
        db.session.delete(token)
    db.session.commit()

    jwt_tokens = create_access_and_refresh_jwt(user)
    return ServiceResult(success=True, data=jwt_tokens)


def logout(
    user: User,
    tokens_to_logout: list,
) -> ServiceResult:
    for token in JWTStore.query.filter_by(user_id=user.id).all():
        if token.jwt_id in tokens_to_logout:
            invalidate_jwt(token.jwt_id, token.type)
            db.session.delete(token)
    db.session.commit()
    return ServiceResult(success=True)


def logout_other_tokens(
    user: User,
    tokens_to_keep: list,
) -> ServiceResult:
    for token in JWTStore.query.filter_by(user_id=user.id).all():
        if token.jwt_id not in tokens_to_keep:
            invalidate_jwt(token.jwt_id, token.type)
            db.session.delete(token)
    db.session.commit()
    return ServiceResult(success=True)


def refresh_token(
    user: User,
    old_refresh_token_jti: str,
) -> ServiceResult:
    old_refresh_token = JWTStore.query.filter_by(
        user_id=user.id, jwt_id=old_refresh_token_jti
    ).one_or_none()
    if old_refresh_token:
        db.session.delete(old_refresh_token)
        db.session.commit()
    invalidate_jwt(old_refresh_token_jti, "refresh")

    jwt_tokens = create_access_and_refresh_jwt(user)
    return ServiceResult(success=True, data=jwt_tokens)


def login_history_w_pagination(
    user: User,
    page: int,
    per_page: int,
) -> ServiceResult:
    data = []
    login_history = (
        LoginHistory.query.filter_by(user_id=user.id)
        .order_by(LoginHistory.datetime.desc())
        .paginate(
            page=page,
            per_page=per_page,
            max_per_page=20,
            count=True,
        )
    )
    for row in login_history:
        data.append(
            {
                "ip": row.ip,
                "user_agent": row.user_agent,
                "datetime": row.datetime,
            }
        )
    result_data = {"total_results": login_history.total, "login_data": data}
    return ServiceResult(success=True, data=result_data)


def roles_list(
    user: User,
) -> ServiceResult:
    data = []
    for role in user.roles:
        data.append({"id": role.id, "name": role.name})
    return ServiceResult(success=True, data=data)
