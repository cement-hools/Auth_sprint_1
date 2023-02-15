import re
import sys

from dotenv import find_dotenv
from loguru import logger as loguru_logger
from pydantic import BaseSettings, Field, PostgresDsn, RedisDsn

logger = loguru_logger
logger.remove()


def obfuscate_message(message: str):
    """Obfuscate sensitive information."""
    result = re.sub(r"'password': '.*'", "'password': [obfuscated]", message)
    return result


def formatter(record):
    record["extra"]["obfuscated_message"] = obfuscate_message(record["message"])
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
