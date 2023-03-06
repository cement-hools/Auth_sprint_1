from http import HTTPStatus

from app.api.v1.roles_authorization import requires_role
from app.services import roles as roles_service
from flask_dantic import serialize
from app.settings.logging import logger
from app.settings.core import user_roles_settings

from flask import Blueprint
from flask_jwt_extended import current_user, jwt_required

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


@router.route("/roles", methods=["GET"])
@requires_role(user_roles_settings.admin)
def all_roles():
    """Список всех ролей."""
    roles = roles_service.roles_list().data
    logger.debug("roles from DB: {}", roles)
    roles = serialize(roles, RoleItem, many=True, json_dump=False)
    logger.debug("serialized roles: {}", roles[:2])
    response_data = RoleListResponse(data=roles)
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles", methods=["POST"])
@requires_role(user_roles_settings.admin)
def create_role():
    """Создание роли."""
    body: CreateRoleRequest = get_body(CreateRoleRequest)
    result = roles_service.create_role(
        name=body.name, description=body.description
    )
    if result.error_message:
        return (
            BaseResponse(success=False, error=result.error_message).dict()
        ), HTTPStatus.BAD_REQUEST

    role_dict = serialize(result.data, RoleItem, json_dump=False)
    role_item = RoleItem(**role_dict)
    response_data = RoleItemResponse(data=role_item)
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>", methods=["GET"])
@requires_role(user_roles_settings.admin)
def detail_role(role_id: str):
    """Получение роли."""
    role = roles_service.role_details(role_id).data
    logger.debug("role from DB: {}", role)
    role_dict = serialize(role, RoleItem, json_dump=False)

    response_data = RoleItemResponse(data=role_dict)
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>", methods=["PUT"])
@requires_role(user_roles_settings.admin)
def edit_role(role_id: str):
    """Редактирование роли."""
    body: UpdateRoleRequest = get_body(UpdateRoleRequest)
    role = roles_service.edit_role(
        role_id=role_id,
        name=body.name,
        description=body.description,
    ).data
    role_dict = serialize(role, RoleItem, json_dump=False)

    response_data = RoleItemResponse(data=role_dict)
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>", methods=["DELETE"])
@requires_role(user_roles_settings.admin)
def delete_role(role_id: str):
    """Удаление роли."""
    result = roles_service.delete_role(role_id)
    return BaseResponse(success=result.success).dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>/add_user", methods=["POST"])
@requires_role(user_roles_settings.admin)
def add_role_to_user(role_id: str):
    """Добавление роли в пользователя."""
    body: AddUserToRoleRequest = get_body(AddUserToRoleRequest)
    result = roles_service.add_role_to_user(role_id, str(body.user_id))
    return BaseResponse(success=result.success).dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>/del_user", methods=["POST"])
@requires_role(user_roles_settings.admin)
def delete_role_from_user(role_id: str):
    """Удаление пользователя из роли."""
    body: DeleteUserFromRoleRequest = get_body(DeleteUserFromRoleRequest)
    result = roles_service.delete_role_from_user(role_id, str(body.user_id))
    return BaseResponse(success=result.success).dict(), HTTPStatus.OK


@router.route(
    "/roles/<string:role_name>/<string:user_id>/check", methods=["GET"]
)
@jwt_required()
def check_user_role(role_name: str, user_id: str):
    """Проверка принадлежности пользователя к роли."""
    if current_user.id == user_id or roles_service.check_user_role(
        user_roles_settings.admin, current_user.id
    ):
        result = roles_service.check_user_role(role_name, user_id)
        return BaseResponse(success=result.success).dict(), HTTPStatus.OK
    else:
        return BaseResponse(success=False).dict(), HTTPStatus.UNAUTHORIZED
