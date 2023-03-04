from models.mixins import BaseModelMixin
from pydantic import UUID4, Field


class Genre(BaseModelMixin):
    id: UUID4 = Field(alias="uuid")


class Person(BaseModelMixin):
    id: UUID4 = Field(alias="uuid")


class PersonShow(Person):
    role: list[str]
    film_ids: list[UUID4]
