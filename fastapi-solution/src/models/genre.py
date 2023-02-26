from typing import Union

from models.filters import BaseSortFilter
from models.mixins import BaseModelMixin
from pydantic import UUID4


class Genre(BaseModelMixin):
    id: Union[UUID4, str]
    name: str | None = None
    description: str | None = None


class GenreSortFilter(BaseSortFilter):
    class Config:
        allowed_filter_field_names = [
            "name",
        ]
