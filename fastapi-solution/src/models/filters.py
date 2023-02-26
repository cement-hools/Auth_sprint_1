from http import HTTPStatus

from fastapi import HTTPException, Query
from pydantic import BaseModel, validator


class BaseSortFilter(BaseModel):
    sort: str | None

    def get_sort_for_elastic(self) -> list:
        # TODO: add support for list of sort fields
        sort = []
        # - descending, + ascending
        if self.sort:
            if self.sort[:1] == "-":
                sort.append(f"{self.sort[1:]}:desc")
            elif self.sort[:1] == "+":
                sort.append(f"{self.sort[1:]}:asc")
            else:
                sort.append(f"{self.sort}:asc")
        return sort

    class Config:
        allowed_filter_field_names = []

    @validator("sort")
    def restrict_sortable_fields(cls, value):
        if value is None:
            return None

        allowed_field_names = cls.Config.allowed_filter_field_names

        # E.g. sort=+-imdb_rating
        if value.count("-") + value.count("+") > 1:
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                f"You tried to sort by '{value}'. "
                "Only one sort order, - or + is allowed, you tried to use more than one.",
            )

        # E.g. sort=imdb_rating-
        if value[1:].count("-") + value[1:].count("+") > 0:
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                f"You tried to sort by '{value}'. "
                f"Sort order is allowed only at start of field name. E.g +{allowed_field_names[0]}",
            )

        field_name = value.replace("+", "").replace("-", "")
        if field_name not in allowed_field_names:
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                f"You tried to sort by '{field_name}',"
                f" but you may only sort by: {', '.join(allowed_field_names)}",
            )

        return value


class PaginationFilter:
    MAX_RESULTS = 10000
    # TODO: переделать пагинацию чтобы работала на больших объемах данных, возможно с search_after
    #  эластика и прочие point in time
    #  https://www.elastic.co/guide/en/elasticsearch/reference/current/paginate-search-results.html

    def __init__(
        self,
        page_size: int = Query(10, alias="page[size]", ge=1, le=1000),
        page_number: int = Query(1, alias="page[number]", ge=1),
    ):
        if page_size * page_number > self.MAX_RESULTS:
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                f"Currently allowing pagination only up to {self.MAX_RESULTS} "
                f"results. You're asking for {page_size * page_number}",
            )
        self.page_size = page_size
        self.page_number = page_number


class QueryFilter:
    def __init__(
        self,
        query: str = Query(
            None,
            description="Search query",
        ),
    ):
        self.query = query
        self.query_fields = []
