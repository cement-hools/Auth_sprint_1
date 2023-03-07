from pydantic import BaseSettings

from app.settings.core import PrimaryConfig


class JaegerSettings(BaseSettings):
    """Настройки Jaeger."""

    host: str = "localhost"
    port: int = 6831
    is_active: bool = True

    class Config(PrimaryConfig):
        env_prefix = "JAEGER_"


jaeger_settings = JaegerSettings()
