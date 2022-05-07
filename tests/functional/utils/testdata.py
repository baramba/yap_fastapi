import json
import os

from config.settings import settings


def read_testdata(filename: str) -> list:
    with open(os.path.join(settings.testdata, filename)) as file:
        es_data = json.load(file)

        obj_data = [
            {key: value for key, value in data.items() if key not in ("_id", "_score", "_index")}
            for data in es_data["hits"]["hits"]
        ]

    return obj_data
