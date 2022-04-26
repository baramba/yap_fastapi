import uuid

from models.basemodel import BaseApiModel



class Genre(BaseApiModel):
    uuid: uuid.UUID
    name: str
