import uuid
from typing import Dict, List, Optional

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Film(BaseModel):
    uuid: uuid.UUID
    imdb_rating: float
    title: str
    description: Optional[str]
    genres: Optional[List[Dict]]
    directors: Optional[List[Dict]]
    actors: Optional[List[Dict]]
    writers: Optional[List[Dict]]

    class Config(object):
        json_loads = orjson.loads
        json_dumps = orjson_dumps
