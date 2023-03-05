from flask import Blueprint

from app.api.v1.oauth import yandex, google

router = Blueprint("oauth", __name__, url_prefix="/oauth")
router.register_blueprint(yandex.router)
router.register_blueprint(google.router)
