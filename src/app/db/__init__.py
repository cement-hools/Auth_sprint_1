from flask import Flask

from settings import pg_settings
from .models import db, Role


def init_db(app: Flask):
    """Инициализация базы данных."""
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = pg_settings.DSN
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return db
