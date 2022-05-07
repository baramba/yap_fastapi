import logging.config
import os
from pathlib import Path

from pydantic import BaseSettings, DirectoryPath, Field, HttpUrl, RedisDsn

from config.logger import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
ROOT_DIR = Path(__file__).parent.parent
print("settings.root:", ROOT_DIR)


class TestSettings(BaseSettings):
    es: HttpUrl = Field(default="http://127.0.0.1:9200", env="TEST_ELASTIC_URL")
    redis_dsn: RedisDsn = Field(default="redis://@localhost:6379/0", env="TEST_REDIS_URL")
    api_url: HttpUrl = Field(default="http://127.0.0.1:8000/api/v1", env="TEST_API_URL")
    api_path: str = Field(default="/api/v1/", env="TEST_API_PATH")

    es_schema: dict = {
        "movies": {"sch_file": "es_movies_schema.json", "data_file": "movies.json"},
        "genres": {"sch_file": "es_genres_schema.json", "data_file": "genres.json"},
        "persons": {"sch_file": "es_persons_schema.json", "data_file": "persons.json"},
    }

    root_dir: DirectoryPath = ROOT_DIR
    testdata: DirectoryPath = Path(os.path.join(ROOT_DIR, "testdata"))


settings = TestSettings()
