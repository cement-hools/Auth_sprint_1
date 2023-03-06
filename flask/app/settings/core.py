from pathlib import Path

from dotenv import find_dotenv
from pydantic import BaseSettings, Field, PostgresDsn, RedisDsn, BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
MIGRATION_DIR = BASE_DIR / "db" / "migrations"


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


class UserRoles(BaseModel):
    """Setting up basic app roles uuids"""

    admin: str = "admin"
    user: str = "user"


flask_settings = FlaskSettings()
pg_settings = PGSettings()
redis_settings = RedisSettings()
user_roles_settings = UserRoles()
