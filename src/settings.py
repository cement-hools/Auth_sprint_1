from loguru import logger as loguru_logger
from pydantic import BaseSettings, Field, PostgresDsn, RedisDsn

logger = loguru_logger


class PrimaryConfig:
    env_file = "../.env.example", "../.env.dev", ".env"
    env_file_encoding = "utf-8"


class FlaskSettings(BaseSettings):
    """Настройки flask."""

    secret_key: str = Field(repr=False)
    debug: bool = Field(default=False)
    host: str = "0.0.0.0"
    port: int = 8000

    class Config(PrimaryConfig):
        env_prefix = "FLASK_"


class PGSettings(BaseSettings):
    """Настройки postgres."""

    dsn: PostgresDsn = Field(repr=False)

    class Config(PrimaryConfig):
        env_prefix = "POSTGRES_"


class RedisSettings(BaseSettings):
    """Настройки Redis."""

    dsn: RedisDsn = Field(repr=False)

    class Config(PrimaryConfig):
        env_prefix = "REDIS_"


flask_settings = FlaskSettings()
pg_settings = PGSettings()
redis_settings = RedisSettings()

logger.debug(flask_settings)
