from typing import Optional, Union

from db.elastic import get_elastic
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from services.base import BaseSearch


class Elastic(BaseSearch):

    async def get_client(self) -> AsyncElasticsearch:
        client = await get_elastic()
        return client

    async def search(self, index: str, size: int, offset: int, search_query: str = None, person_id: str = None, genre: str = None, sort: str = None) -> Optional[Union[list, dict]]:
        client = await self.get_client()

        query = {"match_all": {}}

        if index == 'movies':
            if genre:
                query = {"nested": {"path": "genre", "query": {"term": {"genre.uuid": genre}}}}

            if search_query:
                query = {"multi_match": {"query": search_query, "fields": ["title", "description"]}}

            if person_id:
                query = {
                    "bool": {
                        "should": [
                            {"nested": {"path": role, "query": {"term": {"{0}.uuid".format(role): person_id}}}}
                            for role in ["actors", "writers", "directors"]
                        ]
                    }
                }

        if index == 'genres':
            if search_query:
                query = {"match": {"name": {"query": search_query, "fuzziness": "AUTO"}}}

        if index == 'persons':
            if search_query:
                query = {"multi_match": {"query": search_query, "fields": ["full_name"]}}

        try:
            res = await client.search(index=index, query=query, sort=sort, size=size, from_=offset)
        except NotFoundError:
            return None

        return [doc["_source"] for doc in res["hits"]["hits"]]

    async def get(self, index: str, id: str) -> Optional[dict]:
        client = await self.get_client()
        try:
            doc = await client.get(index=index, id=id)
        except NotFoundError:
            return None
        return doc["_source"]
