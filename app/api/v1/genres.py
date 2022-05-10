import uuid
from http import HTTPStatus
from typing import List, Optional

from api.v1.api_utils import APIMessages, Page
from models.genre import Genre
from services.genres import GenreService, get_genre_service

from fastapi.exceptions import HTTPException
from fastapi.param_functions import Query
from fastapi.params import Depends
from fastapi.routing import APIRouter

router = APIRouter()


class CommParams:
    def __init__(self, genre_service: GenreService = Depends(get_genre_service)) -> None:
        self.genre_service = genre_service


@router.get("/", response_model=List[Genre])
async def genres_all(commons: CommParams = Depends(), page: Page = Depends()) -> Optional[List[Genre]]:
    genres = await commons.genre_service.get_genres(page=page.number, size=page.size)

    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=APIMessages.GENRES_NOT_FOUND)
    return [Genre(**genre) for genre in genres]


@router.get("/search", response_model=list[Genre])
async def genres_search(
    commons: CommParams = Depends(),
    page: Page = Depends(),
    query: str = Query(..., min_length=2),
):
    genres = await commons.genre_service.get_genres_search(query, page.size, page.number)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=APIMessages.GENRES_NOT_FOUND)
    return [Genre(**genre) for genre in genres]


@router.get("/{genre_id}")
async def genre_by_id(genre_id: uuid.UUID, commons: CommParams = Depends()) -> Optional[Genre]:
    genre = await commons.genre_service.get_genre(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=APIMessages.GENRE_NOT_FOUND)
    return Genre(**genre)
