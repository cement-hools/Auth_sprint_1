import uuid

from app.api.v1.schemas import BaseResponse
from pydantic import BaseModel


class RoleItem(BaseModel):
    """Роль."""

    id: uuid.UUID
    name: str
    description: str


class CreateRoleRequest(BaseModel):
    """Запрос на создание роли."""

    name: str
    description: str


class RoleListResponse(BaseResponse):
    """Ответ на запрос всех ролей."""

    data: list[RoleItem]


class RoleItemResponse(BaseResponse):
    """Ответ с информацией о роли."""

    data: RoleItem
