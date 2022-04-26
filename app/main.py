import aioredis
import uvicorn
from api.v1 import films, genres, persons
from core import config
from db import elastic, redis
from elasticsearch import AsyncElasticsearch

from fastapi.applications import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis = await aioredis.from_url(config.REDIS_URL)
    elastic.es = AsyncElasticsearch(hosts=[config.ELASTIC_URL])


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


# Подключаем роутер к серверу, указав префикс /v1/films
# Теги указываем для удобства навигации по документации
app.include_router(films.router, prefix="/api/v1/films", tags=["film"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genre"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["person"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
    )
