import uuid
from enum import Enum
from http import HTTPStatus
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from api.v1.api_utils import Page
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Query
from fastapi.params import Depends
from fastapi.routing import APIRouter
from services.films import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    """Response model for Film."""

    uuid: uuid.UUID
    title: str
    imdb_rating: float
    description: Optional[str]
    genre: Optional[List[Dict]]
    actors: Optional[List[Dict]]
    writers: Optional[List[Dict]]
    directors: Optional[List[Dict]]


class CommParams(object):
    def __init__(self, film_service: FilmService = Depends(get_film_service)) -> None:
        self.film_service = film_service


class SortType(Enum):
    imdb_rating = {"par": "-imdb_rating", "sort": "imdb_rating:desc"}
    default = {"par": "default", "sort": "_doc:desc"}


def sort_param(sort: Optional[str] = Query(SortType.default.value["sort"], regex="^-imdb_rating$")) -> str:
    if sort == SortType.imdb_rating.value["par"]:
        return SortType.imdb_rating.value["sort"]
    return SortType.default.value["sort"]


@router.get("/{film_id}/", response_model=Film)
async def film_details(
    film_id: str,
    commons: CommParams = Depends(),
) -> Film:

    film = await commons.film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return Film(
        uuid=film.uuid,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genre=film.genres,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors,
    )


@router.get("/", response_model=List[Film])
async def films(
    sort: str = Depends(sort_param),
    commons: CommParams = Depends(),
    page: Page = Depends(),
    genre: uuid.UUID = Query(None, alias="filter[genre]"),
) -> List[Film]:

    films_r = await commons.film_service.get_films(sort, page.size, page.number, genre)
    if not films_r:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    return [
        Film(
            uuid=film.uuid,
            title=film.title,
            imdb_rating=film.imdb_rating,
            description=film.description,
            genre=film.genres,
            actors=film.actors,
            writers=film.writers,
            directors=film.directors,
        )
        for film in films_r
    ]


@router.get("/search", response_model=List[Film])
async def films_search(
    commons: CommParams = Depends(),
    page: Page = Depends(),
    query: str = Query(..., min_length=2),
) -> List[Film]:

    films = await commons.film_service.get_films_search(query, page.number, page.size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    return [
        Film(
            uuid=film.uuid,
            title=film.title,
            imdb_rating=film.imdb_rating,
            description=film.description,
            genre=film.genres,
            actors=film.actors,
            writers=film.writers,
            directors=film.directors,
        )
        for film in films
    ]
