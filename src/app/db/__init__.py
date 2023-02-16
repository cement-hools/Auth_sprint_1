from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from settings import pg_settings

db = SQLAlchemy()


def init_db(app: Flask):
    """Инициализация базы данных."""
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = pg_settings.dsn
    db.init_app(app)
    with app.app_context():
        from .models import JWTStore, Role, User

        db.create_all()
    return db
