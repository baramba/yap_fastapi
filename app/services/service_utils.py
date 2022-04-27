from enum import Enum
from http import HTTPStatus

from fastapi.exceptions import HTTPException


class ServiceMessages(Enum):
    ES_ERROR_LOC = "page[number] and page[size]"
    ES_ERROR_MSG_ES = "page[number]+page[size]*page[number] more then 10000"


def get_es_from_value(page: int, size: int) -> int:
    """get_es_from_value return "from" parameter value for ElasticSearch.search().

    Arguments:
        page -- page number
        size -- size of page

    Raises:
        HTTPException: UNPROCESSABLE_ENTITY

    Returns:
        return ElasticSearch.search "from" value
    """
    # https://www.elastic.co/guide/en/elasticsearch/reference/8.1/paginate-search-results.html
    if size + page * size > 10000:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "loc": ["query", ServiceMessages.ES_ERROR_LOC],
                    "msg": ServiceMessages.ES_ERROR_MSG_ES,
                    "type": "value_error",
                    "ctx": {"limit_value": 10000},
                },
            ],
        )
    return page * size





