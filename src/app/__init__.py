from flask import Flask

from settings import flask_settings
from .db import init_db
from .api import v1


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = flask_settings.secret_key

    app.register_blueprint(v1.bp)

    db = init_db(app)
    app.app_context().push()
    db.create_all()

    return app
