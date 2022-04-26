import uuid
from typing import List, Optional
from uuid import UUID

from models.basemodel import BaseApiModel


class Person(BaseApiModel):
    """Model for Person."""

    uuid: uuid.UUID
    full_name: str
    role: str
    film_ids: List[UUID]
