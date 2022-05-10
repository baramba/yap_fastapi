import uuid
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class MetaBaseModel(BaseModel):
    def __lt__(self, other):
        return self.uuid.int < other.uuid.int

    def __le__(self, other):
        return self.uuid.int <= other.uuid.int

    def __gt__(self, other):
        return self.uuid.int > other.uuid.int

    def __ge__(self, other):
        return self.uuid.int >= other.uuid.int


class Film(MetaBaseModel):
    uuid: uuid.UUID
    imdb_rating: float
    title: str
    description: Optional[str]
    genre: Optional[list[dict]]
    directors: Optional[list[dict]]
    actors: Optional[list[dict]]
    writers: Optional[list[dict]]


class FilmBrief(MetaBaseModel):
    uuid: uuid.UUID
    imdb_rating: float
    title: str


class Genre(MetaBaseModel):
    uuid: uuid.UUID
    name: str


class Person(MetaBaseModel):
    uuid: uuid.UUID
    full_name: str
    role: str
    film_ids: list[UUID]
