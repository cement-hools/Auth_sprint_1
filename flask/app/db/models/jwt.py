import uuid

from app.db import db
from sqlalchemy import UUID, ForeignKey

from .user import User


class JWTStore(db.Model):
    __tablename__ = "jwt_store"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        comment="id записи",
    )

    jwt_id = db.Column(db.String(36), nullable=False, index=True)
    expiration_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(UUID, ForeignKey(User.id))
    type = db.Column(db.String(32), nullable=False)
