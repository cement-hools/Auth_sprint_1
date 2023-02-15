from dotenv import find_dotenv
from pydantic import AnyUrl, BaseSettings


class TestSettings(BaseSettings):
    api_service_url: AnyUrl = "http://0.0.0.0:8000"
    api_v1_base_path: str = "/api/v1/"


test_settings = TestSettings(
    _env_file=find_dotenv(), _env_file_encoding="utf-8"
)
