from fastapi.param_functions import Query
from fastapi.params import Depends

class Page(object):
    def __init__(
        self,
        size: int = Query(10, alias="page[size]", ge=1),
        number: int = Query(0, alias="page[number]", ge=0),
    ) -> None:

        self.number = number
        self.size = size