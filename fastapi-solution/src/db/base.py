from abc import ABC, abstractmethod
from typing import Any


class AsyncFulltextSearch(ABC):
    db: Any

    @abstractmethod
    async def get_by_id(self, index: str, id: str):
        pass

    @abstractmethod
    async def get_many_with_query_filter_sort_pagination(
            self, index, query, index_filter, sort, pagination
    ):
        pass

    @abstractmethod
    async def close(self):
        pass
