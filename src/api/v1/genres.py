import uuid
from enum import Enum
from http import HTTPStatus
from typing import List, Optional

from pydantic import BaseModel

from fastapi.exceptions import HTTPException
from fastapi.param_functions import Query
from fastapi.params import Depends
from fastapi.routing import APIRouter
from models.genre import Genre
from services.genres import GenreService, get_genre_service

router = APIRouter()


class CommParams(object):
    def __init__(self, genre_service: GenreService = Depends(get_genre_service)) -> None:
        self.genre_service = genre_service


@router.get("/")
async def genres(commons: CommParams = Depends()) -> Optional[List[Genre]]:
    genres_ = await commons.genre_service.get_genres()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genres not found")
    return genres_