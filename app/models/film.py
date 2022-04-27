import uuid
from typing import Dict, List, Optional

from models.basemodel import BaseApiModel


class Film(BaseApiModel):
    uuid: uuid.UUID
    imdb_rating: float
    title: str
    description: Optional[str]
    genre: Optional[List[Dict]]
    directors: Optional[List[Dict]]
    actors: Optional[List[Dict]]
    writers: Optional[List[Dict]]


class FilmBrief(BaseApiModel):
    uuid: uuid.UUID
    imdb_rating: float
    title: str
