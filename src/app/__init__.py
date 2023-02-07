from flask import Flask

from settings import flask_settings, pg_settings
from .db import db
from .api import v1


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = flask_settings.secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = pg_settings.db_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.register_blueprint(v1.bp)
    db.init_app(app)

    with app.app_context():
        db.create_all()
    return app
