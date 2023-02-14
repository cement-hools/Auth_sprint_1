from flask import Flask

from settings import flask_settings

from .api import v1
from .db import init_db


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = flask_settings.secret_key

    app.register_blueprint(v1.bp)

    init_db(app)

    return app
