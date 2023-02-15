import uuid

from app.db import db
from sqlalchemy import UUID


class Role(db.Model):
    """Роль пользователя."""

    __tablename__ = "roles"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        comment="id записи",
    )
    name = db.Column(db.String, unique=True, nullable=False, comment="Название роли")
    description = db.Column(db.String, nullable=False, comment="Описание роли")
    users = db.relationship("User", secondary="user_role", back_populates="roles")

    def __repr__(self):
        return f"<Role: {self.name}>"
