import os
from logging import config as logging_config

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv("PROJECT_NAME", "movies")

# Настройки Redis
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PROTO = os.getenv("REDIS_PROTO", "redis")
# redis://[[username]:[password]]@localhost:6379/0
REDIS_URL = "{0}://{1}:{2}".format(REDIS_PROTO, REDIS_HOST, REDIS_PORT)

# Настройки Elasticsearch
ELASTIC_PROTO = os.getenv("ELASTIC_PROTO", "http")
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "127.0.0.1")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))
ELASTIC_URL = "{0}://{1}:{2}".format(ELASTIC_PROTO, ELASTIC_HOST, ELASTIC_PORT)

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
