from http import HTTPStatus

from flask import Blueprint, jsonify

router = Blueprint("role", __name__)


@router.route("/roles", methods=["GET"])
def all_roles():
    """Список всех ролей."""
    return jsonify(message="detail_role!"), HTTPStatus.OK


@router.route("/roles", methods=["POST"])
def create_role():
    """Создание роли."""
    return jsonify(message="create_role!"), HTTPStatus.OK


@router.route("/roles/<role_id>", methods=["GET"])
def detail_role(role_id: str):
    """Получение роли."""
    return jsonify(message="detail_role!"), HTTPStatus.OK


@router.route("/roles/<role_id>", methods=["PUT"])
def edit_role(role_id: str):
    """Редактирование роли."""
    return jsonify(message="edit_role!"), HTTPStatus.OK


@router.route("/roles/<role_id>", methods=["DELETE"])
def delete_role(role_id: str):
    """Удаление роли."""
    return jsonify(message="delete_role!"), HTTPStatus.OK
