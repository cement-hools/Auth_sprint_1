import secrets
import string
from datetime import datetime

from flask import request

from app.api.v1.oauth.schemas import yandex
from app.db import db
from app.db.models import LoginHistory, Role, SocialAccount
from app.services.auth import login, registration
from app.services.auth_utils import create_access_and_refresh_jwt
from settings import user_roles_settings


def login_yandex_user(account_user: yandex.User):
    """OAuth Яндекс пользователя."""
    social_account = SocialAccount.query.filter(
        SocialAccount.social_id == account_user.id,
        SocialAccount.social_name == account_user.social_name,
    ).first()
    if not social_account:
        alphabet = string.ascii_letters + string.digits
        password = "".join(secrets.choice(alphabet) for _ in range(10))
        user = registration(
            login=account_user.login,
            email=account_user.email,
            password=password,
        ).data
        admin_role_name = user_roles_settings.admin
        user_role = Role.query.filter(Role.name == admin_role_name).first()
        user.roles.append(user_role)
        account = SocialAccount(
            social_id=account_user.id,
            social_name=account_user.social_name,
            user_id=user.id,
        )

        db.session.add(account)
        db.session.commit()
        jwt_tokens = login(user.login, password).data
        return jwt_tokens

    user = social_account.user
    jwt_tokens = create_access_and_refresh_jwt(user)
    login_history = LoginHistory(
        user_id=user.id,
        ip=request.environ.get("HTTP_X_REAL_IP", request.remote_addr),
        user_agent=request.headers.get("User-Agent"),
        datetime=datetime.now(),
    )
    db.session.add(login_history)
    db.session.commit()
    return jwt_tokens
