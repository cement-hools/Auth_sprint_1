from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis

from settings import flask_settings, jwt_settings, redis_settings

jwt_redis_blocklist = FlaskRedis()


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

    jwt = JWTManager(app)

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """
        Serializes user for storing in a JWT token.
        """
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """
        Coverts user from a JWT token into User object.
        """
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        """
        Callback function to check if a JWT exists in the redis blocklist.
        """
        jti = jwt_payload["jti"]
        token_in_redis = jwt_redis_blocklist.get(jti)
        return token_in_redis is not None

    app.register_blueprint(v1.bp)

    init_db(app)

    return app


# Imports in the bottom to prevent circular dependency error.
from app.db.models.user import User  # noqa

from .api import v1  # noqa
from .db import init_db  # noqa
