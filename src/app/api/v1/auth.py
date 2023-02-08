from http import HTTPStatus

from flask import jsonify, Blueprint

router = Blueprint('auth', __name__)


@router.route('/login', methods=['GET'])
def login():
    return jsonify(message='hello world!'), HTTPStatus.OK
