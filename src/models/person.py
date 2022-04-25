import uuid
from typing import List, Optional
from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Person(BaseModel):
    """Model for Person."""

    uuid: uuid.UUID
    full_name: str
    role: str
    film_ids: List[UUID]

    class Config(object):
        json_loads = orjson.loads
        json_dumps = orjson_dumps
