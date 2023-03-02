from typing import Union

from models.filters import BaseSortFilter
from models.mixins import BaseModelMixin
from pydantic import UUID4


class Person(BaseModelMixin):
    id: Union[UUID4, str]
    full_name: str | None = None


class PersonSortFilter(BaseSortFilter):

    class Config:
        allowed_filter_field_names = ['full_name', ]
