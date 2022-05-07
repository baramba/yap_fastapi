import json
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, ValidationError, parse_obj_as

from config.settings import settings
from utils.structures import Film, FilmBrief, Genre, Person

# class ModelEnum(str, Enum):
#     Film: BaseModel = "Film"
#     FilmBrief: BaseModel = "FilmBrief"
#     Genre: BaseModel = "Genre"
#     Person: BaseModel = "Person"


# class DataForTesting(BaseModel):
#     method: str
#     params: Optional[dict] = None
#     model: Union[Film, FilmBrief, Genre, Person]
#     status: int
#     count: int


# with open(settings.root_dir / "src/api_test_data.json") as file:
#     try:
#         # api_test_data = [DataForTesting.parse_obj(item) for item in json.load(file)]
#         api_test_data = parse_obj_as(list[DataForTesting], json.load(file))
#     except ValidationError as e:
#         print(e.json())


api_test_data = [
    # movies
    {"method": "/films", "params": None, "model": FilmBrief, "status": 200, "count": 10},
    {"method": "/films/search", "params": {"query": "star"}, "model": FilmBrief, "status": 200, "count": 10},
    {"method": "/films/2a090dde-f688-46fe-a9f4-b781a985275e", "params": None, "model": Film, "status": 200, "count": 1},
    # genres
    {"method": "/genres", "params": None, "model": Genre, "status": 200, "count": 10},
    # persons
    {"method": "/persons/search", "params": {"query": "Lucas"}, "model": Person, "status": 200, "count": 1},
    {
        "method": "/persons/fe2b0699-b5ac-437a-9a69-e747b11eb641",
        "params": None,
        "model": Person,
        "status": 200,
        "count": 1,
    },
    {
        "method": "/persons/fc9f27d2-aaee-46e6-b263-40ec8d2dd355/film",
        "params": None,
        "model": FilmBrief,
        "status": 200,
        "count": 5,
    },
]
