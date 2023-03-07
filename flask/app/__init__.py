from datetime import timedelta

from authlib.integrations.flask_client import OAuth
from flask import Flask

from app.jwt_app import jwt, jwt_redis_blocklist
from app.utils import after_request_log, before_request_log
from cli_commands import create_user
from app.settings.core import (
    flask_settings,
    redis_settings,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from app.settings.auth import jwt_settings
from app.settings.oauth import OAuthYandexSettings, OAuthGoogleSettings
from app.settings.logging import logger, InterceptHandler
from .jaeger_app import jaeger

oauth = OAuth()

# Rate limiting
limiter = Limiter(
    get_remote_address,
    storage_uri=redis_settings.dsn,
    storage_options={"socket_connect_timeout": 30},
    default_limits=[flask_settings.global_rate_limiting_option],
    headers_enabled=True,
)


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config["JSON_AS_ASCII"] = False
    app.config["SECRET_KEY"] = flask_settings.secret_key

    # Logging
    app.logger.addHandler(InterceptHandler())

    # JWT
    app.config["JWT_SECRET_KEY"] = jwt_settings.secret_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        hours=jwt_settings.access_token_expires_hours
    )
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(
        days=jwt_settings.refresh_token_expires_days
    )
    app.config["REDIS_URL"] = redis_settings.dsn

    jwt_redis_blocklist.init_app(app, decode_responses=True)
    jwt.init_app(app)

    # Route request logging
    app.before_request(before_request_log)
    app.after_request(after_request_log)

    # Routing
    app.register_blueprint(v1.bp)

    # Jaeger
    jaeger.init_app(app)

    # DB
    init_db(app)

    # CLI
    app.cli.add_command(create_user)

    # OAuth providers init
    app.config.update(OAuthYandexSettings().dict())
    app.config.update(OAuthGoogleSettings().dict())
    oauth.init_app(app)
    oauth.register(name="yandex")
    oauth.register(
        name="google",
        server_metadata_url=OAuthGoogleSettings().CONF_URL,
        client_kwargs={"scope": OAuthGoogleSettings().scope},
    )

    # App is behind one proxy (nginx) that sets the -For and host headers.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

    # Rate limiting
    app.config["RATELIMIT_STRATEGY"] = "fixed-window-elastic-expiry"
    limiter.init_app(app)

    return app


# Imports in the bottom to prevent circular dependency error.
from app.db.models.user import User  # noqa

from .api import v1  # noqa
from .db import init_db  # noqa
