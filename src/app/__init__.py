from datetime import timedelta

from flask import Flask

from app.jwt_app import jwt, jwt_redis_blocklist
from settings import flask_settings, jwt_settings, redis_settings


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = flask_settings.secret_key
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

    app.register_blueprint(v1.bp)

    init_db(app)

    return app


# Imports in the bottom to prevent circular dependency error.
from app.db.models.user import User  # noqa

from .api import v1  # noqa
from .db import init_db  # noqa
