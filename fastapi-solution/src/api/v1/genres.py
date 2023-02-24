from http import HTTPStatus
from typing import Union

from core.config import settings
from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from models.filters import PaginationFilter, QueryFilter
from models.genre import Genre
from pydantic import UUID4, BaseModel
from services.genre import GenreService, get_genre_service

router = APIRouter()


class SingleGenreAPIResponse(BaseModel):
    id: Union[UUID4, str]
    name: str | None = None
    description: str | None = None


# Pydantic supports the creation of generic models
@router.get('', response_model=list[Genre] | None)
@router.get('/search', response_model=list[Genre] | None)
@cache(expire=settings.cache_expiration_in_seconds)
async def genre_list(
        query_filter: QueryFilter = Depends(),
        pagination_filter: PaginationFilter = Depends(),
        genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre] | None:
    """
    Gets a list of genres.
    :param pagination_filter: pagination filter
    :param query_filter: genre filter
    :param genre_service: genre service
    :return: list[Genre] | None
    """
    items = await genre_service.get_many_with_query_filter_sort_pagination(
        query=query_filter,
        pagination=pagination_filter,
    )
    return items


@router.get('/{genre_id}', response_model=SingleGenreAPIResponse)
@cache(expire=settings.cache_expiration_in_seconds)
async def genre_details(
        genre_id: str,
        genre_service: GenreService = Depends(get_genre_service),
) -> SingleGenreAPIResponse:
    """
    Gets a single genre by its ID.
    :param genre_id: id
    :param genre_service: service
    :return: SingleGenreAPIResponse
    """
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"id: '{genre_id}' is not found"
        )
    return SingleGenreAPIResponse(**genre.dict())
