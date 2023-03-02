from functools import wraps

from flask_jwt_extended import current_user, verify_jwt_in_request

from flask import abort


def _has_roles_or_abort(roles):
    verify_jwt_in_request()

    user_roles = current_user.roles

    if not any(role.name in roles for role in user_roles):
        abort(403, "Access denied")


def requires_role(roles):
    """Checks JWT is valid and user has any required role."""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            _has_roles_or_abort(roles)
            return f(*args, **kwargs)

        return wrapper

    return decorator


def requires_admin():
    _has_roles_or_abort(["admin"])
