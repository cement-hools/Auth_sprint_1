from http import HTTPStatus

from app.db import db, models
from flask import Blueprint, request
from flask_dantic import serialize
from settings import logger

from ..schemas import BaseResponse
from ..utils import get_body
from .schemas import (
    CreateRoleRequest,
    RoleItem,
    RoleItemResponse,
    RoleListResponse,
    UpdateRoleRequest,
)

router = Blueprint("role", __name__)

ROLE_404_MESSAGE = "Role not found"


@router.route("/roles", methods=["GET"])
def all_roles():
    """Список всех ролей."""
    logger.info("GET {}", request.path)
    roles = models.Role.query.all()
    logger.debug("roles from DB: {}", roles)
    roles = serialize(roles, RoleItem, many=True, json_dump=False)
    logger.debug("serialized roles: {}", roles[:2])
    response_data = RoleListResponse(data=roles)
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles", methods=["POST"])
def create_role():
    """Создание роли."""
    logger.info("POST {}", request.path)
    logger.debug("request: {}", request.get_json())
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
    logger.info("POST /roles - OK")
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>", methods=["GET"])
def detail_role(role_id: str):
    """Получение роли."""
    logger.info("GET {}", request.path)
    role = db.get_or_404(models.Role, role_id, description=ROLE_404_MESSAGE)
    logger.debug("role from DB: {}", role)
    role_dict = serialize(role, RoleItem, json_dump=False)

    response_data = RoleItemResponse(data=role_dict)
    logger.info("GET {} - OK", request.path)
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>", methods=["PUT"])
def edit_role(role_id: str):
    """Редактирование роли."""
    logger.info("PUT {}", request.path)
    logger.debug("request: {}".format(request.json))
    body: UpdateRoleRequest = get_body(UpdateRoleRequest)
    role = db.get_or_404(models.Role, role_id, description=ROLE_404_MESSAGE)

    role.name = body.name
    role.description = body.description
    db.session.commit()
    role_dict = serialize(role, RoleItem, json_dump=False)

    response_data = RoleItemResponse(data=role_dict)
    logger.info("PUT {} - OK", request.path)
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>", methods=["DELETE"])
def delete_role(role_id: str):
    """Удаление роли."""
    logger.info("DELETE {}", request.path)
    role = db.get_or_404(models.Role, role_id, description=ROLE_404_MESSAGE)
    db.session.delete(role)
    db.session.commit()
    logger.info("DELETE {} - OK", request.path)
    return BaseResponse(success=True).dict(), HTTPStatus.OK
