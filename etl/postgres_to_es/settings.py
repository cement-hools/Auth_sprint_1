from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    only_one_etl_cycle: bool = True

    postgres_dsn: PostgresDsn

    bulk_size: int
    time_loop: int
    sqlite_db_path: str = "db.sqlite"

    elastic_dsn: str

    show_index_name: str = "shows"
    genre_index_name: str = "genres"
    person_index_name: str = "persons"

    indexes: list = [show_index_name, genre_index_name, person_index_name]

    es_common_index_settings: dict = {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_",
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english",
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english",
                },
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_",
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian",
                },
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer",
                    ],
                },
            },
        },
    }

    class Config:
        env_prefix = "FA_"


settings = Settings()
