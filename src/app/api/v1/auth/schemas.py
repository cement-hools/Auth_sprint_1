from datetime import datetime as datetime_type
from ipaddress import IPv4Address, IPv6Address
from typing import Any, Optional, Union

from pydantic import UUID4, BaseModel, EmailStr, Field, validator


class ChangePasswordUserRequest(BaseModel):
    old_password: str = Field(..., title="Old Password")
    new_password: str = Field(
        ..., title="New Password", min_length=6, max_length=72
    )


class LoginHistoryData(BaseModel):
    ip: Union[IPv4Address, IPv6Address] = Field(..., title="Ip")
    user_agent: Optional[Any] = Field(None, title="user_agent")
    datetime: datetime_type = Field(..., title="Datetime")


class LoginUserRequest(BaseModel):
    login: str = Field(..., title="Login")
    password: str = Field(..., title="Password", min_length=6, max_length=72)


class LoginUserResData(BaseModel):
    access_token: str = Field(..., title="Access token")
    access_token_expiration_date: datetime_type = Field(
        ..., title="Access token expiration datetime"
    )
    refresh_token: str = Field(..., title="Refresh token")
    refresh_token_expiration_date: datetime_type = Field(
        ..., title="Refresh token expiration datetime"
    )


class LogoutUser(BaseModel):
    refresh_token: str = Field(..., title="Refresh Token")


class RegUserRequest(BaseModel):
    login: str = Field(..., title="Login")
    email: EmailStr = Field(..., title="Email")
    password: str = Field(..., title="Password", min_length=6, max_length=72)

    @validator("login")
    def login_alphanumeric(cls, v):
        assert v.isalnum(), "must be alphanumeric"
        return v


class RoleData(BaseModel):
    id: UUID4 = Field(..., title="Id")
    name: str = Field(..., title="Name")
