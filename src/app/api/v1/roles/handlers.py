from http import HTTPStatus

from flask import Blueprint
from flask_dantic import serialize

from app.api.v1.roles_authorization import requires_admin
from app.db import db, models
from settings import logger

from ..schemas import BaseResponse
from ..utils import get_body
from .schemas import (
    AddUserToRoleRequest,
    CreateRoleRequest,
    DeleteUserFromRoleRequest,
    RoleItem,
    RoleItemResponse,
    RoleListResponse,
    UpdateRoleRequest,
)

router = Blueprint("role", __name__)

ROLE_404_MESSAGE = "Role not found"


# Admin role required for all routes in this blueprint
router.before_request(requires_admin)


@router.route("/roles", methods=["GET"])
def all_roles():
    """Список всех ролей."""
    roles = models.Role.query.all()
    logger.debug("roles from DB: {}", roles)
    roles = serialize(roles, RoleItem, many=True, json_dump=False)
    logger.debug("serialized roles: {}", roles[:2])
    response_data = RoleListResponse(data=roles)
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles", methods=["POST"])
def create_role():
    """Создание роли."""
    body: CreateRoleRequest = get_body(CreateRoleRequest)
    role_in_db = models.Role.query.filter_by(name=body.name).first()
    if role_in_db:
        error_message = "Role with this name already exists"
        return (
            BaseResponse(success=False, error=error_message).dict()
        ), HTTPStatus.BAD_REQUEST

    role = models.Role(**body.dict())
    db.session.add(role)
    db.session.commit()
    role_dict = serialize(role, RoleItem, json_dump=False)
    role_item = RoleItem(**role_dict)
    response_data = RoleItemResponse(data=role_item)
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>", methods=["GET"])
def detail_role(role_id: str):
    """Получение роли."""
    role = db.get_or_404(models.Role, role_id, description=ROLE_404_MESSAGE)
    logger.debug("role from DB: {}", role)
    role_dict = serialize(role, RoleItem, json_dump=False)

    response_data = RoleItemResponse(data=role_dict)
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>", methods=["PUT"])
def edit_role(role_id: str):
    """Редактирование роли."""
    body: UpdateRoleRequest = get_body(UpdateRoleRequest)
    role = db.get_or_404(models.Role, role_id, description=ROLE_404_MESSAGE)

    role.name = body.name
    role.description = body.description
    db.session.commit()
    role_dict = serialize(role, RoleItem, json_dump=False)

    response_data = RoleItemResponse(data=role_dict)
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>", methods=["DELETE"])
def delete_role(role_id: str):
    """Удаление роли."""
    role = db.get_or_404(models.Role, role_id, description=ROLE_404_MESSAGE)
    db.session.delete(role)
    db.session.commit()
    return BaseResponse(success=True).dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>/add_user", methods=["POST"])
def add_role_to_user(role_id: str):
    """Добавление роли в пользователя."""
    body: AddUserToRoleRequest = get_body(AddUserToRoleRequest)
    user_id = body.user_id
    user_role = models.UserRole.query.filter_by(
        user_id=user_id, role_id=role_id
    ).first()
    if user_role:
        error_message = "User already has this role"
        return (
            BaseResponse(success=False, error=error_message).dict()
        ), HTTPStatus.BAD_REQUEST

    role = db.get_or_404(models.Role, role_id, description=ROLE_404_MESSAGE)
    user = db.get_or_404(models.User, user_id, description=ROLE_404_MESSAGE)
    role.users.append(user)
    db.session.commit()
    response_data = BaseResponse()
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>/del_user", methods=["POST"])
def delete_role_from_user(role_id: str):
    """Удаление пользователя из роли."""
    body: DeleteUserFromRoleRequest = get_body(DeleteUserFromRoleRequest)
    user_id = body.user_id
    user_role = models.UserRole.query.filter_by(
        user_id=user_id, role_id=role_id
    ).first()
    if not user_role:
        error_message = "User does not have this role"
        return (
            BaseResponse(success=False, error=error_message).dict()
        ), HTTPStatus.BAD_REQUEST

    role = db.get_or_404(models.Role, role_id, description=ROLE_404_MESSAGE)
    user = db.get_or_404(models.User, user_id, description=ROLE_404_MESSAGE)
    role.users.remove(user)
    db.session.commit()
    response_data = BaseResponse()
    return response_data.dict(), HTTPStatus.OK


@router.route(
    "/roles/<string:role_id>/<string:user_id>/check", methods=["GET"]
)
def check_user_role(role_id: str, user_id: str):
    """Проверка принадлежности пользователя к роли."""
    user_role = models.UserRole.query.filter_by(
        user_id=user_id, role_id=role_id
    ).first()
    logger.debug("user_role: {}", user_role)
    if not user_role:
        error_message = "User does not have this role"
        return (
            BaseResponse(success=False, error=error_message).dict()
        ), HTTPStatus.BAD_REQUEST
    response_data = BaseResponse()
    return response_data.dict(), HTTPStatus.OK
