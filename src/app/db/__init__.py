from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from settings import pg_settings, user_roles_settings

db = SQLAlchemy()


def init_db(app: Flask):
    """Инициализация базы данных."""
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = pg_settings.dsn
    db.init_app(app)
    with app.app_context():
        from .models import JWTStore, Role, User

        db.create_all()
        db.session.merge(
            Role(
                id=user_roles_settings.uuids["admin"],
                name="Administrator",
                description="Big boss",
            )
        )
        db.session.merge(
            Role(
                id=user_roles_settings.uuids["user"],
                name="User",
                description="Regular user",
            )
        )
        db.session.commit()
    return db
