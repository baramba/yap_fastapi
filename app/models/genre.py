import uuid

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Genre(BaseModel):
    uuid: uuid.UUID
    name: str

    class Config(object):
        json_loads = orjson.loads
        json_dumps = orjson_dumps
