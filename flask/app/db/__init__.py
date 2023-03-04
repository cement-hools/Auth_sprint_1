from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from settings import MIGRATION_DIR, pg_settings
from sqlalchemy import MetaData

from flask import Flask

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)


def init_db(app: Flask):
    """Инициализация базы данных."""
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = pg_settings.dsn
    db.init_app(app)
    Migrate(app, db, MIGRATION_DIR)

    return db
