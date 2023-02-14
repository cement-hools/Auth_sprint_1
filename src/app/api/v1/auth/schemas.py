from datetime import datetime as datetime_type
from ipaddress import IPv4Address, IPv6Address
from typing import Any, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, SecretStr


class ChangePasswordUserRequest(BaseModel):
    login: str = Field(..., title="login")
    new_password: SecretStr = Field(..., title="New Password")


class HistoryData(BaseModel):
    ip: Union[IPv4Address, IPv6Address] = Field(..., title="Ip")
    user_agent: Optional[Any] = Field(None, title="user_agent")
    datetime: datetime_type = Field(..., title="Datetime")


class HistoryResponse(BaseModel):
    success: Optional[bool] = Field(True, title="Success")
    error: Optional[str] = Field("", title="Error")
    data: List[HistoryData] = Field(..., title="Data")


class LoginUserRequest(BaseModel):
    login: str = Field(..., title="Login")
    password: SecretStr = Field(..., title="Password")


class LoginUserResData(BaseModel):
    login: str = Field(..., title="Login")
    token: str = Field(..., title="Token")
    datetime: datetime_type = Field(..., title="Datetime")


class LoginUserResponse(BaseModel):
    success: Optional[bool] = Field(True, title="Success")
    error: Optional[str] = Field("", title="Error")
    data: LoginUserResData


class LogoutAllUser(BaseModel):
    login: str = Field(..., title="Login")


class LogoutUser(BaseModel):
    refresh_token: str = Field(..., title="Refresh Token")


class RefreshToken(BaseModel):
    user_id: str = Field(..., title="User Id")
    refresh_token: str = Field(..., title="Refresh Token")


class RefreshTokenData(BaseModel):
    refresh_token: str = Field(..., title="Refresh Token")
    access_token: str = Field(..., title="Access Token")


class RefreshTokenResponse(BaseModel):
    success: Optional[bool] = Field(True, title="Success")
    error: Optional[str] = Field("", title="Error")
    data: RefreshTokenData


class RegUserRequest(BaseModel):
    login: str = Field(..., title="Login")
    email: EmailStr = Field(..., title="Email")
    password: SecretStr = Field(..., title="Password")


class RegUserResponse(BaseModel):
    success: Optional[bool] = Field(True, title="Success")
    error: Optional[str] = Field("", title="Error")
    data: RegUserRequest


class RoleData(BaseModel):
    id: str = Field(..., title="Id")
    name: str = Field(..., title="Name")


class UsersRoleResponse(BaseModel):
    success: Optional[bool] = Field(True, title="Success")
    error: Optional[str] = Field("", title="Error")
    data: List[RoleData] = Field(..., title="Data")
