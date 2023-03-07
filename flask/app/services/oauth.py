import secrets
import string

from app.api.v1.oauth.schemas import yandex, google
from app.db import db
from app.db.models import SocialAccount
from app.db.models.user import User
from app.services.auth import login, registration
from app.services.schemas import ServiceResult
from app.settings.logging import logger


SOCIAL_NAME = SocialAccount.SocialName


def _create_random_alphanumeric_string():
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(30))


def _social_login_or_register(
    email: str,
    social_id: str,
    social_name: SOCIAL_NAME,
    social_login: str = None,
):
    social_account = SocialAccount.query.filter(
        SocialAccount.social_id == social_id,
        SocialAccount.social_name == social_name,
    ).first()

    if not social_account:  # Need to create social account
        logger.debug(
            "Social account for {} social_id = {} not found",
            social_name,
            social_id,
        )

        # Trying to log in with email to see if user with this email already registered
        login_attempt = login(
            login=None, email=email, password=None, is_social_auth=True
        )
        logger.debug(
            "Login attempt with just email is successful: {}",
            login_attempt.success,
        )

        if login_attempt.success:
            user = User.query.filter_by(email=email).one_or_none()
        else:  # We do not have an account with this email, try to create
            registration_attempt = registration(
                login=social_login or _create_random_alphanumeric_string(),
                email=email,
                password=_create_random_alphanumeric_string(),
            )
            logger.debug(
                "Registration attempt with just email is successful: {}",
                registration_attempt.success,
            )
            if registration_attempt.success:
                user = registration_attempt.data
            else:
                return registration_attempt

        # Creating social account entry
        social_account = SocialAccount(
            social_id=social_id,
            social_name=social_name,
            user_id=user.id,
        )
        db.session.add(social_account)
        db.session.commit()
        logger.debug(
            "Created social account for {}. social_id = {}, user.id = {}",
            social_name,
            social_id,
            user.id,
        )

    return login(social_account.user.login, None, is_social_auth=True)


def login_yandex_user(account_user: yandex.User):
    """OAuth Яндекс пользователя."""
    yandex_name = SOCIAL_NAME.YANDEX
    return _social_login_or_register(
        email=account_user.email,
        social_id=account_user.id,
        social_name=yandex_name,
        social_login=account_user.login,
    )


def login_google_user(token: google.Token):
    if not token.email_verified:
        error_message = "Need to verify email in Google first"
        return ServiceResult(success=False, error_message=error_message)
    google_name = SOCIAL_NAME.GOOGLE
    return _social_login_or_register(
        email=token.email,
        social_id=token.sub,
        social_name=google_name,
    )
