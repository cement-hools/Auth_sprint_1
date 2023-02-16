import uuid

from flask_bcrypt import check_password_hash, generate_password_hash
from sqlalchemy import UUID

from app.db import db

from .role import Role


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
        db.String,
        unique=True,
        nullable=False,
        index=True,
        comment="Логин пользователя",
    )
    email = db.Column(db.String, nullable=False, comment="Email пользователя")
    password_hash = db.Column(
        db.String(128), nullable=False, comment="Хэш пароля пользователя"
    )
    login_history = db.relationship("LoginHistory", backref="user")
    roles = db.relationship(
        "Role", secondary="user_role", back_populates="users"
    )
    jwts = db.relationship("JWTStore", backref="user", lazy="dynamic")

    def __repr__(self):
        return f"<User: {self.login}>"

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password).decode("utf8")

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


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
    user_agent = db.Column(
        db.String, nullable=False, comment="User-Agent пользователя"
    )
    datetime = db.Column(
        db.DateTime, nullable=False, comment="Дата и время входа"
    )

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
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id))
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey(Role.id))
