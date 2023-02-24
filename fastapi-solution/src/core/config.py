import logging
from logging import config as logging_config

from core.logger import LOGGING
from dotenv import find_dotenv
from pydantic import BaseSettings, RedisDsn

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class EsIndexes(BaseSettings):
    show_index_name: str = 'shows'
    genre_index_name: str = 'genres'
    person_index_name: str = 'persons'

    service_index_map = {
        'show': show_index_name,
        'genre': genre_index_name,
        'person': person_index_name,
    }


class Elastic(BaseSettings):
    # Настройки Elasticsearch
    elastic_dsn: str
    search_fuzziness: int | str = 'AUTO'  # Will break search tests if changed


class Redis(BaseSettings):
    # Настройки Redis
    redis_dsn: RedisDsn
    cache_expiration_in_seconds: int


class Settings(EsIndexes, Elastic, Redis, BaseSettings):
    # Название проекта. Используется в Swagger-документации
    project_name: str = 'Practix'

    log_level: int = logging.DEBUG
    logging_config: dict = LOGGING

    gunicorn_bind_host: str
    gunicorn_bind_port: str

    api_v1_base_path: str = '/api/v1'


settings = Settings(_env_file=find_dotenv(), _env_file_encoding='utf-8')
