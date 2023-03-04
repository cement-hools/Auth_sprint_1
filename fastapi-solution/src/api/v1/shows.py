from http import HTTPStatus

from app.settings.core import settings
from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from models.filters import PaginationFilter, QueryFilter
from models.show import Show, ShowGenreFilter, ShowSortFilter
from services.show import ShowService, get_show_service

router = APIRouter()


class SingleShowAPIResponse(Show):
    pass


# TODO: документировать параметры
@router.get("", response_model=list[Show] | None)
@router.get("/search", response_model=list[Show] | None)
@cache(expire=settings.cache_expiration_in_seconds)
async def show_list(
    query_filter: QueryFilter = Depends(),
    show_sort_filter: ShowSortFilter = Depends(),
    show_genre_filter: ShowGenreFilter = Depends(),
    pagination_filter: PaginationFilter = Depends(),
    show_service: ShowService = Depends(get_show_service),
) -> list[Show] | None:
    """
    Gets a list of genres.
    :param query_filter:
    :param pagination_filter:
    :param show_service: service
    :param show_genre_filter: show genre filter
    :param show_sort_filter: show sort filter
    :return: list[Show] | None
    """
    items = await show_service.get_many_with_query_filter_sort_pagination(
        query=query_filter,
        index_filter=show_genre_filter,
        sort=show_sort_filter,
        pagination=pagination_filter,
    )
    return items


@router.get("/{show_id}", response_model=SingleShowAPIResponse)
@cache(expire=settings.cache_expiration_in_seconds)
async def show_details(
    show_id: str,
    show_service: ShowService = Depends(get_show_service),
) -> SingleShowAPIResponse:
    """
    Gets a single show by its ID.
    :param show_id: id
    :param show_service: service
    :return: SingleShowAPIResponse
    """
    show = await show_service.get_by_id(show_id)
    if not show:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Show not found"
        )
    return SingleShowAPIResponse(**show.dict())
