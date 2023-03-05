from pydantic import BaseSettings, Field, PostgresDsn, RedisDsn
from .core import PrimaryConfig


class JWTSettings(BaseSettings):
    """Настройки JWT."""

    secret_key: str = Field(repr=False)
    access_token_expires_hours: int = Field(default=1)
    refresh_token_expires_days: int = Field(default=30)

    class Config(PrimaryConfig):
        env_prefix = "JWT_"


jwt_settings = JWTSettings()
