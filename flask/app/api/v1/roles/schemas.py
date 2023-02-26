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


class UpdateRoleRequest(CreateRoleRequest):
    """Запрос на изменение роли."""


class AddUserToRoleRequest(BaseModel):
    """Добавить пользователя в роль."""

    user_id: uuid.UUID


class DeleteUserFromRoleRequest(AddUserToRoleRequest):
    """Удалить пользователя из роли."""


class RoleListResponse(BaseResponse):
    """Ответ на запрос всех ролей."""

    data: list[RoleItem]


class RoleItemResponse(BaseResponse):
    """Ответ с информацией о роли."""

    data: RoleItem
