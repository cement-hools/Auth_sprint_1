from flask import Blueprint

from app.api.v1.oauth import yandex

router = Blueprint("oauth", __name__, url_prefix="/oauth")
router.register_blueprint(yandex.router)
