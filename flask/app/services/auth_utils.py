from datetime import datetime

from app import jwt_redis_blocklist
from app.api.v1.auth.schemas import LoginUserResData
from app.db import db, models
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jti,
)

from flask import current_app


def create_access_and_refresh_jwt(user: models.User) -> LoginUserResData:
    access_token = create_access_token(identity=user)
    access_token_expiration_date = (
        datetime.now() + current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    )

    refresh_token = create_refresh_token(identity=user)
    refresh_token_expiration_date = (
        datetime.now() + current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
    )

    # Saving token ids to DB
    # (allows for logout all, and JWT invalidation during password change)
    db.session.add(
        models.JWTStore(
            jwt_id=get_jti(access_token),
            expiration_date=access_token_expiration_date,
            user_id=user.id,
            type="access",
        )
    )
    db.session.add(
        models.JWTStore(
            jwt_id=get_jti(refresh_token),
            expiration_date=refresh_token_expiration_date,
            user_id=user.id,
            type="refresh",
        )
    )
    db.session.commit()

    return LoginUserResData(
        access_token=access_token,
        access_token_expiration_date=access_token_expiration_date,
        refresh_token=refresh_token,
        refresh_token_expiration_date=refresh_token_expiration_date,
    )


def invalidate_jwt(jti, token_type):
    if token_type == "access":
        expiration_date = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    elif token_type == "refresh":
        expiration_date = current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
    jwt_redis_blocklist.set(jti, "", ex=expiration_date)
