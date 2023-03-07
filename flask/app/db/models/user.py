import enum
import uuid

from flask_bcrypt import check_password_hash, generate_password_hash
from sqlalchemy import UUID, UniqueConstraint, Enum

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
        db.String(72),
        unique=True,
        nullable=False,
        index=True,
        comment="Логин пользователя",
    )
    email = db.Column(
        db.String(320), nullable=False, comment="Email пользователя"
    )
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

    def verify_password(self, password=None):
        if not password:
            return False
        return check_password_hash(self.password_hash, password)


class SocialAccount(db.Model):
    """Аккаунт в социальной сети."""

    __tablename__ = "social_accounts"
    __table_args__ = (
        db.UniqueConstraint("social_id", "social_name", name="social_pk"),
    )

    class SocialName(enum.Enum):
        """Название социальной сети"""

        YANDEX = "yandex"
        GOOGLE = "google"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False,
    )
    user = db.relationship(
        User, backref=db.backref("social_accounts", lazy=True)
    )
    social_id = db.Column(db.String(128), nullable=False)
    social_name = db.Column(
        Enum(
            SocialName,
            name="social_name_type",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )

    def __repr__(self):
        return f"<SocialAccount {self.social_name}:{self.user_id}>"


def create_partition(target, connection, **kw) -> None:
    """creating partition by user_sign_in"""
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_in_tablet"    # noqa W291
        PARTITION OF "login_history" FOR VALUES IN ('tablet')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_in_mobile"    # noqa W291
        PARTITION OF "login_history" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_in_web"       # noqa W291
        PARTITION OF "login_history" FOR VALUES IN ('web')"""
    )


class LoginHistory(db.Model):
    """История входа пользователя."""

    __tablename__ = "login_history"
    __table_args__ = (
        UniqueConstraint("id", "user_device_type"),
        {
            "postgresql_partition_by": "LIST (user_device_type)",
            "listeners": [("after_create", create_partition)],
        },
    )

    class DeviceType:
        """Тип устройства."""

        PC = "web"
        MOBILE = "mobile"
        TABLET = "tablet"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="id Записи",
    )
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey(User.id, ondelete="CASCADE")
    )
    ip = db.Column(db.String(45), nullable=False, comment="IP пользователя")
    user_agent = db.Column(
        db.Text, nullable=False, comment="User-Agent пользователя"
    )
    user_device_type = db.Column(db.String(255), primary_key=True)
    datetime = db.Column(
        db.DateTime, nullable=False, comment="Дата и время входа"
    )

    def __repr__(self):
        return f"<LoginHistory: (User: {self.user_id}, {self.datetime}>"


class UserRole(db.Model):
    """Связь пользователя и роли."""

    __tablename__ = "user_role"
    __table_args__ = (db.UniqueConstraint("user_id", "role_id"),)

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey(User.id, ondelete="CASCADE")
    )
    role_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey(Role.id, ondelete="CASCADE")
    )
