import pytest

from config.settings import settings
from utils.structures import Film, FilmBrief, Genre, Person
from utils.testdata import read_testdata


@pytest.fixture(scope="session")
def get_genres():
    genres: list = read_testdata(settings.es_schema["genres"]["data_file"])
    return [Genre(**genre) for genre in genres]


@pytest.fixture(scope="session")
def get_persons():
    persons: list = read_testdata(settings.es_schema["persons"]["data_file"])
    return [Person(**person) for person in persons]


@pytest.fixture(scope="session")
def get_movies():
    movies: list = read_testdata(settings.es_schema["movies"]["data_file"])
    return [Film(**movie) for movie in movies]


@pytest.fixture(scope="session")
def get_movies_brief():
    movies: list = read_testdata(settings.es_schema["movies"]["data_file"])
    return [FilmBrief(**movie) for movie in movies]
