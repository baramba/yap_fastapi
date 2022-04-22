import uuid
from enum import Enum
from http import HTTPStatus
from typing import List, Optional

from pydantic import BaseModel

from fastapi.exceptions import HTTPException
from fastapi.param_functions import Query
from fastapi.params import Depends
from fastapi.routing import APIRouter
from services.films import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    uuid: uuid.UUID
    title: str
    imdb_rating: float


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


class Page(object):
    def __init__(
        self,
        size: int = Query(10, alias="page[size]", ge=1),
        number: int = Query(0, alias="page[number]", ge=0),
    ) -> None:

        self.number = number
        self.size = size


@router.get("/{film_id}", response_model=Film)
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
    )


@router.get("/", response_model=List[Film])
async def films(
    sort: str = Depends(sort_param),
    commons: CommParams = Depends(),
    page: Page = Depends(),
    genre: uuid.UUID = Query(None, alias="filter[genre]"),
) -> List[Film]:

    films = await commons.film_service.get_films(sort, page.size, page.number, genre)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")
    ret_films = []
    for film in films:
        ret_films.append(
            Film(
                uuid=film.uuid,
                title=film.title,
                imdb_rating=film.imdb_rating,
            ),
        )
    return ret_films
