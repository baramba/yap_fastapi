import uuid
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Film(BaseModel):
    uuid: uuid.UUID
    imdb_rating: float
    title: str
    description: Optional[str]
    genre: Optional[list[dict]]
    directors: Optional[list[dict]]
    actors: Optional[list[dict]]
    writers: Optional[list[dict]]


class FilmBrief(BaseModel):
    uuid: uuid.UUID
    imdb_rating: float
    title: str


class Genre(BaseModel):
    uuid: uuid.UUID
    name: str


class Person(BaseModel):
    uuid: uuid.UUID
    full_name: str
    role: str
    film_ids: list[UUID]
