from http import HTTPStatus

from app.db import db, models
from flask import Blueprint, jsonify, request
from flask_dantic import serialize
from psycopg2 import errors
from pydantic import ValidationError
from settings import logger
from sqlalchemy.exc import IntegrityError

from ..schemas import BaseResponse
from .schemas import CreateRoleRequest, RoleItem, RoleItemResponse, RoleListResponse

UniqueViolation = errors.lookup("23505")

router = Blueprint("role", __name__)


@router.route("/roles", methods=["GET"])
def all_roles():
    """Список всех ролей."""
    logger.info("GET {}", request.path)
    try:
        roles = models.Role.query.all()
        logger.debug("roles from DB: {}", roles)
        roles = serialize(roles, RoleItem, many=True, json_dump=False)
        logger.debug("serialized roles: {}", roles[:2])
    except Exception as err:
        logger.error("{}: {}", err.__class__.__name__, err)
        error_message = str(err)
        return (
            BaseResponse(success=False, error=error_message).dict(),
        ), HTTPStatus.INTERNAL_SERVER_ERROR

    response_data = RoleListResponse(data=roles)
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles", methods=["POST"])
def create_role():
    """Создание роли."""
    logger.info("POST {}", request.path)
    logger.debug("request: {}".format(request.json))
    try:
        body = CreateRoleRequest(**request.json)

        role = models.Role(**body.dict())
        db.session.add(role)
        db.session.commit()
        role_dict = serialize(role, RoleItem, json_dump=False)
    except ValidationError as err:
        logger.error("{}: {}", err.__class__.__name__, err)
        error_message = err.errors()
        return (
            BaseResponse(success=False, error=error_message).dict()
        ), HTTPStatus.BAD_REQUEST
    except Exception as err:
        logger.error("{}: {}", err.__class__.__name__, err)
        error_message = str(err)
        if isinstance(err, IntegrityError) and isinstance(err.orig, UniqueViolation):
            error_message = "Role with this name already exists"
        return (
            BaseResponse(success=False, error=error_message).dict()
        ), HTTPStatus.INTERNAL_SERVER_ERROR
    role_item = RoleItem(**role_dict)
    response_data = RoleItemResponse(data=role_item)
    logger.info("POST /roles - OK")
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>", methods=["GET"])
def detail_role(role_id: str):
    """Получение роли."""
    logger.info("GET {}", request.path)
    try:
        role = models.Role.query.get(role_id)
        logger.debug("role from DB: {}", role)
        role_dict = serialize(role, RoleItem, json_dump=False)
    except Exception as err:
        logger.error("{}: {}", err.__class__.__name__, err)
        error_message = str(err)
        return (
            BaseResponse(success=False, error=error_message).dict(),
        ), HTTPStatus.INTERNAL_SERVER_ERROR
    logger.info("GET {} - OK", request.path)
    if not role:
        return (
            BaseResponse(success=False, error="Role not found").dict(),
            HTTPStatus.NOT_FOUND,
        )
    response_data = RoleItemResponse(data=role_dict)
    return response_data.dict(), HTTPStatus.OK


@router.route("/roles/<string:role_id>", methods=["PUT"])
def edit_role(role_id: str):
    """Редактирование роли."""
    return jsonify(message="edit_role!"), HTTPStatus.OK


@router.route("/roles/<string:role_id>", methods=["DELETE"])
def delete_role(role_id: str):
    """Удаление роли."""
    db.session.delete(models.Role.query.get(role_id))
    db.session.commit()
    return jsonify(message="delete_role!"), HTTPStatus.OK
