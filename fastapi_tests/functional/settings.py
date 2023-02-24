from dotenv import find_dotenv
from pydantic import BaseSettings, RedisDsn


class EsIndexes(BaseSettings):
    show_index_name: str = 'shows'
    genre_index_name: str = 'genres'
    person_index_name: str = 'persons'

    index_names: list = [
        show_index_name,
        genre_index_name,
        person_index_name,
    ]


class EsBackup(BaseSettings):
    repo_name: str = 'test_repo'
    snapshot_name: str = 'test_snapshot'


class Elastic(BaseSettings):
    # Настройки Elasticsearch
    elastic_dsn: str = 'http://127.0.0.1:9200'


class Redis(BaseSettings):
    # Настройки Redis
    redis_dsn: RedisDsn = 'redis://127.0.0.1:6379'


class TestSettings(EsIndexes, EsBackup, Elastic, Redis, BaseSettings):
    api_service_url: str = 'http://0.0.0.0:8000'
    api_v1_base_path: str = '/api/v1/'


test_settings = TestSettings(_env_file=find_dotenv(), _env_file_encoding='utf-8')
