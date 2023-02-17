from dotenv import find_dotenv
from pydantic import AnyUrl, BaseSettings, PostgresDsn


class TestSettings(BaseSettings):
    api_service_url: AnyUrl = "http://0.0.0.0:5000"
    api_v1_base_path: str = "/api/v1/"

    postgres_dsn: PostgresDsn


test_settings = TestSettings(
    _env_file=find_dotenv(filename=".env.dev"), _env_file_encoding="utf-8"
)
