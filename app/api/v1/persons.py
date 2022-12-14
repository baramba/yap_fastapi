import logging
import uuid
from enum import Enum
from http import HTTPStatus
from typing import List, Optional

from api.v1.api_utils import APIMessages, Page
from models.film import FilmBrief
from models.person import Person
from services.persons import PersonService, get_person_service

from fastapi.exceptions import HTTPException
from fastapi.param_functions import Query
from fastapi.params import Depends
from fastapi.routing import APIRouter

router = APIRouter()


class CommParams:
    def __init__(self, person_service: PersonService = Depends(get_person_service)) -> None:
        self.person_service = person_service


@router.get(
    "/{person_id}/film",
    response_model=List[FilmBrief],
    deprecated=True,
    description=APIMessages.OLD_ANDOID_DEVICE.value,
)
async def persons_films(
    person_id: uuid.UUID, commons: CommParams = Depends(), page: Page = Depends()
) -> Optional[List[FilmBrief]]:
    films = await commons.person_service.get_films_by_person(person_id, page.size, page.number)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=APIMessages.FILMS_NOT_FOUND)
    return films


@router.get("/search", response_model=List[Person])
async def persons_search(
    commons: CommParams = Depends(), page: Page = Depends(), query: str = Query(..., min_length=2)
) -> Optional[List[Person]]:
    person = await commons.person_service.get_persons_search(query, page.size, page.number)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=APIMessages.PERSON_NOT_FOUND)
    return person


@router.get("/{person_id}")
async def person_by_id(person_id: uuid.UUID, commons: CommParams = Depends()) -> Optional[Person]:
    person = await commons.person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=APIMessages.PERSON_NOT_FOUND)
    return person
