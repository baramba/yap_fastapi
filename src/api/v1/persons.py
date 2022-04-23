import uuid
from enum import Enum
from http import HTTPStatus
from typing import List, Optional

from pydantic import BaseModel

from api.v1.api_utils import Page
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Query
from fastapi.params import Depends
from fastapi.routing import APIRouter
from models.person import Person
from services.persons import PersonService, get_person_service

router = APIRouter()


class CommParams(object):
    def __init__(self, person_service: PersonService = Depends(get_person_service)) -> None:
        self.person_service = person_service


@router.get("/search")
async def persons(
    commons: CommParams = Depends(), page: Page = Depends(), query: str = Query(..., min_length=2)
) -> Optional[List[Person]]:
    persons_ = await commons.person_service.get_persons_search(query, page.size, page.number)
    if not persons_:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="persons not found")
    return persons_
