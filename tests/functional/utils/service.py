from typing import Union

from pydantic import BaseModel


def validate(
    data: Union[list[Union[bytes, dict]], Union[bytes, dict]], model: BaseModel
) -> Union[list[BaseModel], BaseModel]:
    if isinstance(data, list):
        if isinstance(data[0], dict):
            return [model.parse_obj(item) for item in data]
        if isinstance(data[0], bytes):
            return [model.parse_raw(item) for item in data]
    else:
        if isinstance(data, dict):
            return model.parse_obj(data)
        if isinstance(data, bytes):
            return model.parse_raw(data)
