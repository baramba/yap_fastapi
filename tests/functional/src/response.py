import logging
from dataclasses import dataclass

from multidict import CIMultiDictProxy
from pydantic import BaseModel


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


class Response:
    def __init__(self, response: HTTPResponse):
        self.response = response
        self.status = response.status
        self.headers = response.headers
        self.body = response.body

    def status_code(self, status_code: int):
        assert self.status == status_code

    def len(self, _len: int):
        count = 0
        if isinstance(self.body, list):
            count = len(self.body)
        if isinstance(self.body, dict):
            count = 1
        assert count == _len

    def validate(self, model: BaseModel):
        if self.status == 200:
            if isinstance(self.body, list):
                for item in self.body:
                    model.parse_obj(item)
            else:
                model.parse_obj(self.body)
