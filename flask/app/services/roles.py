from app.db import db
from app.db.models.role import Role
from app.db.models.user import User, UserRole

from .schemas import ServiceResult

ROLE_404_MESSAGE = "Role not found"
USER_404_MESSAGE = "User not found"


def roles_list() -> ServiceResult:
    roles = Role.query.all()
    return ServiceResult(success=True, data=roles)


def create_role(
    name: str,
    description: str,
) -> ServiceResult:
    role_in_db = Role.query.filter_by(name=name).first()
    if role_in_db:
        error_message = "Role with this name already exists"
        return ServiceResult(success=False, error_message=error_message)

    role = Role(name=name, description=description)
    db.session.add(role)
    db.session.commit()
    return ServiceResult(success=True, data=role)


def role_details(
    role_id: str,
) -> ServiceResult:
    role = db.get_or_404(Role, role_id, description=ROLE_404_MESSAGE)
    return ServiceResult(success=True, data=role)


def edit_role(
    role_id: str,
    name: str,
    description: str,
) -> ServiceResult:
    role = db.get_or_404(Role, role_id, description=ROLE_404_MESSAGE)
    role.name = name
    role.description = description
    db.session.commit()
    return ServiceResult(success=True, data=role)


def delete_role(
    role_id: str,
) -> ServiceResult:
    role = db.get_or_404(Role, role_id, description=ROLE_404_MESSAGE)
    db.session.delete(role)
    db.session.commit()
    return ServiceResult(success=True)


def add_role_to_user(
    role_id: str,
    user_id: str,
) -> ServiceResult:
    user_role = UserRole.query.filter_by(
        user_id=user_id, role_id=role_id
    ).first()
    if user_role:
        error_message = "User already has this role"
        return ServiceResult(success=False, error_message=error_message)

    role = db.get_or_404(Role, role_id, description=ROLE_404_MESSAGE)
    user = db.get_or_404(User, user_id, description=USER_404_MESSAGE)
    role.users.append(user)
    db.session.commit()
    return ServiceResult(success=True)


def delete_role_from_user(
    role_id: str,
    user_id: str,
) -> ServiceResult:
    user_role = UserRole.query.filter_by(
        user_id=user_id, role_id=role_id
    ).first()
    if not user_role:
        error_message = "User does not have this role"
        return ServiceResult(success=False, error_message=error_message)

    role = db.get_or_404(Role, role_id, description=ROLE_404_MESSAGE)
    user = db.get_or_404(User, user_id, description=USER_404_MESSAGE)
    role.users.remove(user)
    db.session.commit()
    return ServiceResult(success=True)


def check_user_role(
    role_name: str,
    user_id: str,
) -> ServiceResult:
    role = Role.query.filter_by(name=role_name).one_or_none()
    if not role:
        error_message = "Role not found"
        return ServiceResult(success=False, error_message=error_message)

    user_role = UserRole.query.filter_by(
        user_id=user_id, role_id=role.id
    ).first()
    if not user_role:
        error_message = "User does not have this role"
        return ServiceResult(success=False, error_message=error_message)
    return ServiceResult(success=True)
