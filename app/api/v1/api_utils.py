from enum import Enum

from fastapi.param_functions import Query
from fastapi.params import Depends


class Page:
    def __init__(
        self,
        size: int = Query(10, alias="page[size]", ge=1),
        number: int = Query(0, alias="page[number]", ge=0),
    ) -> None:

        self.number = number
        self.size = size


class APIMessages(str, Enum):
    FILM_NOT_FOUND = "film not found"
    FILMS_NOT_FOUND = "films not found"

    GENRES_NOT_FOUND = "genres not found"
    GENRE_NOT_FOUND = "genre not found"

    OLD_ANDOID_DEVICE = "used for old android devices"
    PERSON_NOT_FOUND = "persons not found"
