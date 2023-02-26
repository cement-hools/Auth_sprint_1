import orjson
from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    # декодируем, чтобы возвращать unicode для pydantic
    return orjson.dumps(v, default=default).decode()


class UUIDMixin(BaseModel):
    uuid: str = Field(alias="id")


class BaseModelMixin(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        allow_population_by_field_name = True
