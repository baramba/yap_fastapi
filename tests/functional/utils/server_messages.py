SORT_ERROR = {
    "detail": [
        {
            "loc": ["query", "sort"],
            "msg": 'string does not match regex "^-imdb_rating$"',
            "type": "value_error.str.regex",
            "ctx": {"pattern": "^-imdb_rating$"},
        }
    ]
}

MIN_LIMIT_PAGE_SIZE_ERROR = {
    "detail": [
        {
            "loc": ["query", "page[size]"],
            "msg": "ensure this value is greater than or equal to 1",
            "type": "value_error.number.not_ge",
            "ctx": {"limit_value": 1},
        }
    ]
}

MAX_LIMIT_PAGE_SIZE_ERROR = {
    "detail": [
        {
            "loc": ["query", "page[size]"],
            "msg": "ensure this value is less than or equal to 10000",
            "type": "value_error.number.not_le",
            "ctx": {"limit_value": 10000},
        }
    ]
}

MIN_LIMIT_PAGE_NUMBER_ERROR = {
    "detail": [
        {
            "ctx": {"limit_value": 0},
            "loc": ["query", "page[number]"],
            "msg": "ensure this value is greater than or equal to 0",
            "type": "value_error.number.not_ge",
        }
    ]
}

MAX_LIMIT_PAGE_NUMBER_ERROR = {
    "detail": [
        {
            "ctx": {"limit_value": 10000},
            "loc": ["query", "page[number] and page[size]"],
            "msg": "page[number]+page[size]*page[number] more then 10000",
            "type": "value_error",
        }
    ]
}

FILTER_GENRE_UUID_ERROR = {
    "detail": [{"loc": ["query", "filter[genre]"], "msg": "value is not a valid uuid", "type": "type_error.uuid"}]
}

FILM_UUID_ERROR = {
    "detail": [{"loc": ["path", "film_id"], "msg": "value is not a valid uuid", "type": "type_error.uuid"}]
}

PERSON_UUID_ERROR = {
    "detail": [{"loc": ["path", "person_id"], "msg": "value is not a valid uuid", "type": "type_error.uuid"}]
}

GENRE_UUID_ERROR = {
    "detail": [{"loc": ["path", "genre_id"], "msg": "value is not a valid uuid", "type": "type_error.uuid"}]
}

EMPTY_QUERY_ERROR = {
    "detail": [
        {
            "loc": ["query", "query"],
            "msg": "ensure this value has at least 2 characters",
            "type": "value_error.any_str.min_length",
            "ctx": {"limit_value": 2},
        }
    ]
}
