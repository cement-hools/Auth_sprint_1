from functools import lru_cache

from core.config import settings
from db.base import AsyncFulltextSearch
from db.elastic import get_async_search
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.filters import PaginationFilter
from models.genre import Genre
from services.base import BaseService


class GenreService(BaseService):
    def __init__(self, async_search_db: AsyncFulltextSearch):
        self.async_search_db = async_search_db
        self.single_item_model = Genre
        self.index_name = settings.service_index_map["genre"]

    async def get_by_id(self, id: str) -> Genre | None:
        item = await self.async_search_db.get_by_id(self.index_name, id)
        if item:
            return self.single_item_model(**item)
        return None

    async def get_many_with_query_filter_sort_pagination(
        self,
        query=None,
        sort=None,
        index_filter=None,
        pagination: PaginationFilter = Depends(),
    ) -> list[Genre] | None:
        if query:
            query.query_fields = [
                "name^2",
                "description^1",
            ]  # Changes here will break search tests
        items = await self.async_search_db.get_many_with_query_filter_sort_pagination(
            self.index_name, query, index_filter, sort, pagination
        )
        if items:
            return [Genre(**item) for item in items]
        return []


@lru_cache()
def get_genre_service(
    async_search_db: AsyncFulltextSearch = Depends(get_async_search),
) -> GenreService:
    return GenreService(async_search_db)
