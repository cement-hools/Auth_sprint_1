from loguru import logger as loguru_logger
from pydantic import BaseSettings, Field, PostgresDsn

logger = loguru_logger


class PrimaryConfig:
    env_file = "../.env.sample", "../.env.dev", ".env"
    env_file_encoding = "utf-8"


class FlaskSettings(BaseSettings):
    """Настройки flask."""

    secret_key: str = Field(repr=False)
    debug: bool = Field(default=False)

    class Config(PrimaryConfig):
        env_prefix = "FLASK_"


class PGSettings(BaseSettings):
    """Настройки postgres."""

    DSN: PostgresDsn = Field(repr=False)

    class Config(PrimaryConfig):
        env_prefix = "POSTGRES_"


flask_settings = FlaskSettings()
pg_settings = PGSettings()

logger.debug(flask_settings)
