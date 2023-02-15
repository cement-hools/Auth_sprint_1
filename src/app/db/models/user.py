import uuid

from app.db import db
from sqlalchemy import UUID


class User(db.Model):
    """Пользователь."""

    __tablename__ = "users"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        comment="id Пользователя",
    )
    login = db.Column(
        db.String, unique=True, nullable=False, comment="Логин пользователя"
    )
    email = db.Column(db.String, nullable=False, comment="email Пользователя")
    password = db.Column(db.String, nullable=False, comment="Пароль Пользователя")
    login_history = db.relationship(
        "LoginHistory", backref="user", comment="История входа"
    )
    roles = db.relationship("Role", secondary="user_role", back_populates="users")

    def __repr__(self):
        return f"<User: {self.login}>"


class LoginHistory(db.Model):
    """История входа пользователя."""

    __tablename__ = "login_history"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        comment="id Записи",
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id))
    ip = db.Column(db.String, nullable=False, comment="IP пользователя")
    user_agent = db.Column(db.String, nullable=False, comment="User-Agent пользователя")
    datetime = db.Column(db.DateTime, nullable=False, comment="Дата и время входа")

    def __repr__(self):
        return f"<LoginHistory: (User: {self.user_id}, {self.datetime}>"


class UserRole(db.Model):
    """Связь пользователя и роли."""

    __tablename__ = "user_role"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"))
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey("roles.id"))
