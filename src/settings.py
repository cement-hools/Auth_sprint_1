import re
import sys

from dotenv import find_dotenv
from loguru import logger as loguru_logger
from pydantic import BaseSettings, Field, PostgresDsn, RedisDsn

logger = loguru_logger
logger.remove()


def obfuscate_message(message: str):
    """Obfuscate sensitive information."""
    result = re.sub(r"password': '.*?'", "password': [obfuscated]", message)
    result = re.sub(r'token": ".*?"', 'token": [obfuscated]', message)
    return result


def formatter(record):
    record["extra"]["obfuscated_message"] = obfuscate_message(
        record["message"]
    )
    return "[{level}] {extra[obfuscated_message]}\n{exception}"


logger.add(sys.stderr, format=formatter)


class PrimaryConfig:
    env_file = [
        find_dotenv(filename=".env"),
        find_dotenv(filename=".env.dev"),  # Has more priority, if found
    ]
    # TODO: При локальном запуске, SQLAlchemy/psycopg2 берет dsn из .env все равно, даже если если есть .env.dev.
    # Это не проблема конфига выше, он работает как ожидается и на вход init_db уходит dsn из .env.dev.
    # Даже если закомментировать здесь импорт .env, SQLAlchemy/psycopg2 все равно подтянет переменные из .env
    env_file_encoding = "utf-8"


class FlaskSettings(BaseSettings):
    """Настройки flask."""

    secret_key: str = Field(repr=False)
    debug: bool = Field(default=False)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=5000)

    class Config(PrimaryConfig):
        env_prefix = "FLASK_"


class JWTSettings(BaseSettings):
    """Настройки JWT."""

    secret_key: str = Field(repr=False)
    access_token_expires_hours: int = Field(default=1)
    refresh_token_expires_days: int = Field(default=30)

    class Config(PrimaryConfig):
        env_prefix = "JWT_"


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


class UserRoles(BaseSettings):
    """Setting up basic app roles uuids"""

    uuids = {
        "admin": "9b751230-c16b-40af-8732-2f0c20961a04",
        "user": "1ac6344c-bb0f-4903-9d2e-9fe182ea7132",
    }


flask_settings = FlaskSettings()
jwt_settings = JWTSettings()
pg_settings = PGSettings()
redis_settings = RedisSettings()
user_roles_settings = UserRoles()

logger.debug(flask_settings)
