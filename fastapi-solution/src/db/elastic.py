from elasticsearch import AsyncElasticsearch, NotFoundError
from db.base import AsyncFulltextSearch
from elasticsearch_dsl import Q, Search
from elasticsearch_dsl.query import MultiMatch
from app.settings.core import settings

es: AsyncFulltextSearch | None = None


async def get_async_search() -> AsyncFulltextSearch:
    return es


class AsyncESearch(AsyncFulltextSearch):
    def __init__(self, db: AsyncElasticsearch):
        self.db = db

    async def get_by_id(self, index: str, id: str):
        """
        Get a single item by its id from index in Elastic.
        :param index:
        :param id:
        :return:
        """
        try:
            doc = await self.db.get(index=index, id=id)
        except NotFoundError:
            return None
        return doc["_source"]

    @classmethod
    def _paginate_es_query(
        self, query: Search, page_size: int, page_number: int
    ) -> Search:
        start = (page_number - 1) * page_size
        return query[start : start + page_size]

    async def get_many_with_query_filter_sort_pagination(
        self, index: str, query, index_filter, sort, pagination
    ):
        if sort is None:
            sort = []
        else:
            sort = sort.get_sort_for_elastic()
        es_query = Search()
        if index_filter and index_filter.genre_id:
            es_query = es_query.filter(
                "nested",
                path="genres",
                query=Q("term", genres__id=index_filter.genre_id),
            )
        if query.query:
            es_query = es_query.query(
                MultiMatch(
                    query=query.query,
                    fields=query.query_fields,
                    fuzziness=settings.search_fuzziness,
                )
            )
        query_body = self._paginate_es_query(
            query=es_query,
            page_size=pagination.page_size,
            page_number=pagination.page_number,
        ).to_dict()
        search = await self.db.search(
            index=index,
            body=query_body,
            sort=sort,
        )
        items = [hit["_source"] for hit in search["hits"]["hits"]]
        return items

    async def close(self):
        await self.db.close()
