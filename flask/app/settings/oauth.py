from pydantic import BaseSettings, AnyUrl
from .core import PrimaryConfig


class OAuthYandexSettings(BaseSettings):
    """Настройки OAuth Яндекс."""

    YANDEX_CLIENT_ID: str
    YANDEX_CLIENT_SECRET: str
    YANDEX_ACCESS_TOKEN_URL: str
    YANDEX_AUTHORIZE_URL: str

    class Config(PrimaryConfig):
        env_prefix = "OAUTH_"


class OAuthGoogleSettings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    CONF_URL: AnyUrl = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )

    class Config(PrimaryConfig):
        env_prefix = "OAUTH_"
