# import json
# from enum import Enum
# from typing import Optional, Union

from config.settings import settings
from utils.structures import Film, FilmBrief, Genre, Person

# from pydantic import BaseModel, ValidationError, parse_obj_as


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
    # films method
    # 1 without params
    {
        "method": "/films",
        "params": None,
        "model": FilmBrief,
        "status": 200,
        "count": 10,
    },
    # 2 with valid sort
    {
        "method": "/films",
        "params": {"sort": "-imdb_rating"},
        "model": FilmBrief,
        "status": 200,
        "count": 10,
    },
    # 3 with empty sort
    {
        "method": "/films",
        "params": {"sort": ""},
        "model": None,
        "status": 422,
        "count": 1,
    },
    # 4 with not valid sort
    {
        "method": "/films",
        "params": {"sort": "-id"},
        "model": None,
        "status": 422,
        "count": 1,
    },
    # 5 with not valid param
    # {
    #     "method": "/films",
    #     "params": {"cort": "-imdb_rating"},
    #     "model": None,
    #     "status": 422,
    #     "count": 1,
    # },
    # 6 with valid filter
    {
        "method": "/films",
        "params": {"filter[genre]": "526769d7-df18-4661-9aa6-49ed24e9dfd8"},
        "model": FilmBrief,
        "status": 200,
        "count": 10,
    },
    # 7 with empty filter
    {
        "method": "/films",
        "params": {"filter[genre]": ""},
        "model": None,
        "status": 422,
        "count": 1,
    },
    # 8 with not valid param filter
    # {
    #     "method": "/films",
    #     "params": {"filter[]": "526769d7-df18-4661-9aa6-49ed24e9dfd8"},
    #     "model": None,
    #     "status": 422,
    #     "count": 1,
    # },
    # 9 with filter and sort
    {
        "method": "/films",
        "params": {"filter[genre]": "526769d7-df18-4661-9aa6-49ed24e9dfd8", "sort": "-imdb_rating"},
        "model": FilmBrief,
        "status": 200,
        "count": 10,
    },
    # 10 with filter and not valid value sort
    {
        "method": "/films",
        "params": {"filter[genre]": "526769d7-df18-4661-9aa6-49ed24e9dfd8", "sort": "imdb_rating"},
        "model": FilmBrief,
        "status": 422,
        "count": 1,
    },
    # 11 with filter and not valid param sort
    # {
    #     "method": "/films",
    #     "params": {"filter[genre]": "526769d7-df18-4661-9aa6-49ed24e9dfd8", "cort": "-imdb_rating"},
    #     "model": FilmBrief,
    #     "status": 422,
    #     "count": 1,
    # },
    # 12 with page[size]=1
    {
        "method": "/films",
        "params": {"page[size]": 1},
        "model": FilmBrief,
        "status": 200,
        "count": 1,
    },
    # 13 with page[size]=0
    {
        "method": "/films",
        "params": {"page[size]": 0},
        "model": None,
        "status": 422,
        "count": 1,
    },
    # 14 with page[size]=10000
    {
        "method": "/films",
        "params": {"page[size]": 10000},
        "model": FilmBrief,
        "status": 200,
        "count": 100,
    },
    # 15 with page[size]=10001
    # {
    #     "method": "/films",
    #     "params": {"page[size]": 10001},
    #     "model": None,
    #     "status": 500,
    #     "count": 0,
    # },
    # 16 with page[number]=0
    {
        "method": "/films",
        "params": {"page[number]": 0},
        "model": FilmBrief,
        "status": 200,
        "count": 10,
    },
    # 17 with page[number]=-1
    {
        "method": "/films",
        "params": {"page[number]": -1},
        "model": None,
        "status": 422,
        "count": 1,
    },
    # 18 with page[number]=9
    {
        "method": "/films",
        "params": {"page[number]": 9},
        "model": FilmBrief,
        "status": 200,
        "count": 10,
    },
    # 19 with page[number]=10
    {
        "method": "/films",
        "params": {"page[number]": 10},
        "model": None,
        "status": 404,
        "count": 1,
    },
    # 19 by valid id
    {
        "method": "/films/2a090dde-f688-46fe-a9f4-b781a985275e",
        "params": None,
        "model": Film,
        "status": 200,
        "count": 1,
    },
    # 20 by not valid id
    {
        "method": "/films/Star_Wars",
        "params": None,
        "model": None,
        "status": 422,
        "count": 1,
    },
    # {
    #     "method": "/films/search",
    #     "params": {"query": "star"},
    #     "model": FilmBrief,
    #     "status": 200,
    #     "count": 10,
    # },
    # #
    # {
    #     "method": "/films/2a090dde-f688-46fe-a9f4-b781a985275e",
    #     "params": None,
    #     "model": Film,
    #     "status": 200,
    #     "count": 1,
    # },
    # # genres
    # {
    #     "method": "/genres",
    #     "params": None,
    #     "model": Genre,
    #     "status": 200,
    #     "count": 10,
    # },
    # # persons
    # {
    #     "method": "/persons/search",
    #     "params": {"query": "Lucas"},
    #     "model": Person,
    #     "status": 200,
    #     "count": 1,
    # },
    # {
    #     "method": "/persons/fe2b0699-b5ac-437a-9a69-e747b11eb641",
    #     "params": None,
    #     "model": Person,
    #     "status": 200,
    #     "count": 1,
    # },
    # {
    #     "method": "/persons/fc9f27d2-aaee-46e6-b263-40ec8d2dd355/film",
    #     "params": None,
    #     "model": FilmBrief,
    #     "status": 200,
    #     "count": 5,
    # },
]
