import uuid
from typing import Optional

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Film(BaseModel):
    uuid: uuid.UUID
    imdb_rating: float
    title: str
    description: Optional[str] = ""
    genres: Optional[tuple] = tuple()
    director: list = list()
    actors: Optional[tuple] = tuple()
    writers: Optional[tuple] = tuple()
    actors_names: list = list()
    writers_names: list = list()
    actors_id: list = []
    writers_id: list = []

    class Config(object):
        json_loads = orjson.loads
        json_dumps = orjson_dumps
