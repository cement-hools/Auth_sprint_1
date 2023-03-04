from app.db.models.user import User
from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis

jwt_redis_blocklist = FlaskRedis()

jwt = JWTManager()


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
