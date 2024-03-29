from abc import ABC, abstractmethod
from elasticsearch import AsyncElasticsearch

from core.config import settings
from db.elastic import AsyncESearch
from db.base import AsyncFulltextSearch


class BaseService(ABC):
    async_search_db: AsyncFulltextSearch
    index_name: str
    single_item_model: type
    elastic: AsyncESearch(AsyncElasticsearch(hosts=[settings.elastic_dsn]))

    @abstractmethod
    async def get_many_with_query_filter_sort_pagination(
        self, query, index_filter, sort, pagination
    ):
        pass

    @abstractmethod
    async def get_by_id(self, id: str):
        """
        Get a single self.single_item_model type item by its id from self.index_name index in Elastic.
        :param id:
        :return:
        """
