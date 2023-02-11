from http import HTTPStatus

from app.db import db
from app.db.models import Role
from flask import Blueprint, jsonify, request
from flask_dantic import serialize
from settings import logger

from ..schemas import BaseResponse
from .schemas import RoleListResponse, RoleScheme

router = Blueprint("role", __name__)


@router.route("/roles", methods=["GET"])
def all_roles():
    """Список всех ролей."""
    logger.info("GET {}", request.path)
    try:
        roles = Role.query.all()
        logger.debug("roles from DB: {}", roles)
        roles = serialize(roles, RoleScheme, many=True, json_dump=False)
        logger.debug("serialized roles: {}", roles[:2])
    except Exception as err:
        logger.error("{}: {}", err.__class__.__name__, err)
        return jsonify(
            BaseResponse(success=False, error=str(err)).dict(),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    response_data = RoleListResponse(data=roles)
    return jsonify(response_data.dict(), HTTPStatus.OK)


@router.route("/roles", methods=["POST"])
def create_role():
    """Создание роли."""
    logger.info("POST /roles")
    logger.debug("request: {}".format(request.json))
    name = request.json.get("name")
    description = request.json.get("description")
    role = Role(name=name, description=description)
    logger.debug("role: {}".format(role.__dict__))
    db.session.add(role)
    db.session.commit()
    logger.info("POST /roles - OK")
    return jsonify(role), HTTPStatus.OK


@router.route("/roles/<string:role_id>", methods=["GET"])
def detail_role(role_id: str):
    """Получение роли."""
    return jsonify(message="detail_role!"), HTTPStatus.OK


@router.route("/roles/string:<role_id>", methods=["PUT"])
def edit_role(role_id: str):
    """Редактирование роли."""
    return jsonify(message="edit_role!"), HTTPStatus.OK


@router.route("/roles/str:<role_id>", methods=["DELETE"])
def delete_role(role_id: str):
    """Удаление роли."""
    return jsonify(message="delete_role!"), HTTPStatus.OK
