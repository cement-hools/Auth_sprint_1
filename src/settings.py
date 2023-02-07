from loguru import logger as loguru_logger
from pydantic import BaseSettings, Field

logger = loguru_logger


class PrimaryConfig:
    env_file = '../.env.sample', '../.env.dev', '.env'
    env_file_encoding = 'utf-8'


class FlaskSettings(BaseSettings):
    """Настройки flask."""
    secret_key: str
    debug: bool = Field(default=False)

    class Config(PrimaryConfig):
        env_prefix = 'FLASK_'


class PGSettings(BaseSettings):
    """Настройки postgres."""
    dbname: str = Field(env='DB_NAME')
    user: str
    password: str = Field(repr=False)
    host: str
    port: int

    def async_db_uri(self):
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.dbname}"
        )

    def db_uri(self):
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.dbname}"
        )

    class Config(PrimaryConfig):
        env_prefix = 'DB_'


flask_settings = FlaskSettings()
pg_settings = PGSettings()

logger.debug(flask_settings)
logger.debug(pg_settings)
