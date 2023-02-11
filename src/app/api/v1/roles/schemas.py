import uuid

from app.api.v1.schemas import BaseResponse
from pydantic import BaseModel


class RoleScheme(BaseModel):
    """Роль."""

    id: uuid.UUID
    name: str
    description: str


class RoleListRequest(BaseModel):
    """Запрос всех ролей."""

    name: str
    description: str


class RoleListResponse(BaseResponse):
    """Ответ на запрос всех ролей."""

    data: list[RoleScheme]
