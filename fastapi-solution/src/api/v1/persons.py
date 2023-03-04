from http import HTTPStatus
from typing import Union

from app.settings.core import settings
from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from models.filters import PaginationFilter, QueryFilter
from models.person import Person
from pydantic import UUID4, BaseModel
from services.person import PersonService, get_person_service

router = APIRouter()


class SinglePersonAPIResponse(BaseModel):
    id: Union[UUID4, str]
    full_name: str | None = None


@router.get("", response_model=list[Person] | None)
@router.get("/search", response_model=list[Person] | None)
@cache(expire=settings.cache_expiration_in_seconds)
async def person_list(
    query_filter: QueryFilter = Depends(),
    pagination_filter: PaginationFilter = Depends(),
    person_service: PersonService = Depends(get_person_service),
) -> list[Person] | None:
    """
    Gets a list of persons.
    :param query_filter:
    :param person_service: service
    :param person_sort_filter: person filter
    :param pagination_filter: pagination filter
    :return: list[Person] | None
    """
    items = await person_service.get_many_with_query_filter_sort_pagination(
        query=query_filter,
        pagination=pagination_filter,
    )
    return items


@router.get("/{person_id}", response_model=SinglePersonAPIResponse)
@cache(expire=settings.cache_expiration_in_seconds)
async def person_details(
    person_id: str,
    person_service: PersonService = Depends(get_person_service),
) -> SinglePersonAPIResponse:
    """
    Gets a single person by its ID.
    :param person_id: id
    :param person_service: service
    :return: SinglePersonAPIResponse
    """
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"id: '{person_id}' is not found",
        )
    return SinglePersonAPIResponse(**person.dict())
