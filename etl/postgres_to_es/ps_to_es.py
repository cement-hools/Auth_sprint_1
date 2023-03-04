from __future__ import annotations

from db_query import full_load, load_person_q, query_all_genre
from pydantic import BaseModel, Field
from app.settings.core import settings


def es_create_show_index(client):
    """Create shows index in Elasticsearch if one isn't already there."""
    client.indices.create(
        index=settings.show_index_name,
        body={
            "settings": settings.es_common_index_settings,
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword",
                    },
                    "imdb_rating": {
                        "type": "float",
                    },
                    "genres": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "id": {
                                "type": "keyword",
                            },
                            "name": {
                                "type": "text",
                                "analyzer": "ru_en",
                            },
                            "description": {
                                "type": "text",
                                "analyzer": "ru_en",
                            },
                        },
                    },
                    "title": {
                        "type": "text",
                        "analyzer": "ru_en",
                        "fields": {
                            "raw": {
                                "type": "keyword",
                            },
                        },
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "ru_en",
                    },
                    "director": {
                        "type": "text",
                        "analyzer": "ru_en",
                    },
                    "actors_names": {
                        "type": "text",
                        "analyzer": "ru_en",
                    },
                    "writers_names": {
                        "type": "text",
                        "analyzer": "ru_en",
                    },
                    "actors": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "id": {
                                "type": "keyword",
                            },
                            "full_name": {
                                "type": "text",
                                "analyzer": "ru_en",
                            },
                        },
                    },
                    "writers": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "id": {
                                "type": "keyword",
                            },
                            "full_name": {
                                "type": "text",
                                "analyzer": "ru_en",
                            },
                        },
                    },
                },
            },
        },
        ignore=400,
    )


def es_create_genre_index(client):
    """Create genres index in Elasticsearch if one isn't already there."""
    client.indices.create(
        index=settings.genre_index_name,
        body={
            "settings": settings.es_common_index_settings,
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword",
                    },
                    "name": {"type": "text", "analyzer": "ru_en"},
                    "description": {"type": "text", "analyzer": "ru_en"},
                },
            },
        },
        ignore=400,
    )


def es_create_person_index(client):
    """Create persons index in Elasticsearch if one isn't already there."""
    client.indices.create(
        index=settings.person_index_name,
        body={
            "settings": settings.es_common_index_settings,
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword",
                    },
                    "full_name": {"type": "text", "analyzer": "ru_en"},
                },
            },
        },
        ignore=400,
    )


class Person(BaseModel):
    id: str
    full_name: str | None = None


class Genre(BaseModel):
    id: str
    name: str | None = None
    description: str | None = None


class EsDataclass(BaseModel):
    class Config:
        allow_population_by_field_name = True

    id: str
    underscore_id: str = Field(alias="_id")  # публичное имя
    imdb_rating: float | None = Field(None, ge=0, le=10)
    genres: list[Genre] | None = None
    title: str | None = None
    description: str | None = None
    director: list[str] | None = None
    actors_names: list[str] | None = None
    writers_names: list[str] | None = None
    actors: list[Person] | None = None
    writers: list[Person] | None = None


class EsDataclassGenre(BaseModel):
    class Config:
        allow_population_by_field_name = True

    id: str
    underscore_id: str = Field(alias="_id")
    name: str | None = None
    description: str | None = None


class EsDataclassPerson(BaseModel):
    class Config:
        allow_population_by_field_name = True

    id: str
    underscore_id: str = Field(alias="_id")
    full_name: str | None = None


def validate_row_create_es_doc(row):
    """Метод преобразования данных из PG в ES построчно"""

    def dict_from_persons_str(string):
        return {
            "id": (string.split(":::"))[0],
            "role": (string.split(":::"))[1],
            "full_name": (string.split(":::"))[2],
        }

    def _genre_from_genres_str(string):
        return Genre(id=string.split(":::")[0], name=string.split(":::")[1])

    if row["persons"][0] is not None:
        persons = [dict_from_persons_str(p) for p in row["persons"]]
        directors = [
            Person(id=p["id"], full_name=p["full_name"])
            for p in persons
            if p["role"] == "director"
        ]
        actors = [
            Person(id=p["id"], full_name=p["full_name"])
            for p in persons
            if p["role"] == "actor"
        ]
        writers = [
            Person(id=p["id"], full_name=p["full_name"])
            for p in persons
            if p["role"] == "writer"
        ]
    else:
        directors = actors = writers = []

    if row["genres"][0] is not None:
        genres = [_genre_from_genres_str(g) for g in row["genres"]]
    else:
        genres = []

    return EsDataclass(
        id=row["id"],
        _id=row["id"],
        imdb_rating=row["imdb_rating"],
        genres=genres,
        title=row["title"],
        description=row["description"],
        director=[p.full_name for p in directors],
        actors_names=[p.full_name for p in actors],
        writers_names=[p.full_name for p in writers],
        actors=actors,
        writers=writers,
    ).dict(by_alias=True)


def validate_row_create_es_doc_genre(row):
    """Метод преобразования жанров из PG в ES построчно"""
    return EsDataclassGenre(
        id=row["id"],
        _id=row["id"],
        name=row["name"],
        description=row["description"],
    ).dict(by_alias=True)


def validate_row_create_es_doc_person(row):
    """Метод преобразования данных из PG в ES построчно"""
    return EsDataclassPerson(
        id=row["id"], _id=row["id"], full_name=row["full_name"]
    ).dict(by_alias=True)


def generate_actions(pg_cursor, last_successful_load):
    """Метод сборки данных об обновленных фильмах"""
    pg_cursor.execute(full_load.format(last_successful_load))
    for row in pg_cursor:
        yield validate_row_create_es_doc(row)


def generate_genre_actions(pg_cursor, last_successful_load):
    """Метод сборки данных об обновленных жанрах"""
    pg_cursor.execute(query_all_genre.format(last_successful_load))
    for row in pg_cursor:
        yield validate_row_create_es_doc_genre(row)


def generate_person_actions(pg_cursor, last_successful_load):
    """Метод сборки данных об обновленных персонах"""
    pg_cursor.execute(load_person_q.format(last_successful_load))
    for row in pg_cursor:
        yield validate_row_create_es_doc_person(row)
