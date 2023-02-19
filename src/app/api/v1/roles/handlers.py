from http import HTTPStatus

from flask import Blueprint
from flask_dantic import serialize

from app.api.v1.roles_authorization import requires_admin
from app.services import roles as roles_service
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

router.before_request(
    requires_admin
)  # Admin role required for all routes in this blueprint


@router.route("/roles", methods=["GET"])
def all_roles():
    """Список всех ролей."""
    roles = roles_service.roles_list()
    logger.debug("roles from DB: {}", roles)
    roles = serialize(roles, RoleItem, many=True, json_dump=False)
    logger.debug("serialized roles: {}", roles[:2])
    response_data = RoleListResponse(data=roles)
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles", methods=["POST"])
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
def detail_role(role_id: str):
    """Получение роли."""
    role = roles_service.role_details(role_id).data
    logger.debug("role from DB: {}", role)
    role_dict = serialize(role, RoleItem, json_dump=False)

    response_data = RoleItemResponse(data=role_dict)
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>", methods=["PUT"])
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
def delete_role(role_id: str):
    """Удаление роли."""
    result = roles_service.delete_role(role_id)
    return BaseResponse(success=result.success).dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>/add_user", methods=["POST"])
def add_role_to_user(role_id: str):
    """Добавление роли в пользователя."""
    body: AddUserToRoleRequest = get_body(AddUserToRoleRequest)
    result = roles_service.add_role_to_user(role_id, str(body.user_id))
    return BaseResponse(success=result.success).dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>/del_user", methods=["POST"])
def delete_role_from_user(role_id: str):
    """Удаление пользователя из роли."""
    body: DeleteUserFromRoleRequest = get_body(DeleteUserFromRoleRequest)
    result = roles_service.delete_role_from_user(role_id, str(body.user_id))
    return BaseResponse(success=result.success).dict(), HTTPStatus.OK


@router.route(
    "/roles/<string:role_id>/<string:user_id>/check", methods=["GET"]
)
def check_user_role(role_id: str, user_id: str):
    """Проверка принадлежности пользователя к роли."""
    result = roles_service.check_user_role(role_id, user_id)
    return BaseResponse(success=result.success).dict(), HTTPStatus.OK
