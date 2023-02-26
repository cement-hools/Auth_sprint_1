from typing import Union

from fastapi import Query
from models.common_models import Genre, Person
from models.filters import BaseSortFilter
from models.mixins import BaseModelMixin
from pydantic import UUID4


class Show(BaseModelMixin):
    id: Union[UUID4, str]
    imdb_rating: float | None = None
    genres: list[Genre | None] = None
    title: str | None = None
    description: str | None = None
    director: list[str] | None = None
    actors_names: list[str] | None = None
    writers_names: list[str] | None = None
    actors: list[Person] | None = None
    writers: list[Person] | None = None


class ShowGenreFilter:
    def __init__(
        self,
        genre_id: str = Query(
            None,
            description="Genre UUID4, which is used to output "
            "only Shows with corresponding genres",
            alias="filter[genre]",
        ),
    ):
        self.genre_id = genre_id


class ShowSortFilter(BaseSortFilter):
    class Config:
        allowed_filter_field_names = ["imdb_rating"]
