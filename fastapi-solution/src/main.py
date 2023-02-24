from http import HTTPStatus

import uvicorn
from api.v1.api import api_router as api_router_v1
from core.config import settings
from db import redis, elastic
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    elastic.es = elastic.AsyncESearch(
        AsyncElasticsearch(
            hosts=[settings.elastic_dsn],
        ),
    )
    redis.redis = aioredis.from_url(
        settings.redis_dsn,
        max_connections=10,
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis.redis), prefix="fastapi-cache")


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


app.include_router(api_router_v1, prefix=settings.api_v1_base_path)


@app.exception_handler(NotFoundError)
async def es_not_found_exception_handler(exc: NotFoundError):
    return ORJSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"message": f"Index not found. If you're testing, you should create or restore indexes first.\n{exc}"},
    )

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.gunicorn_bind_host,
        port=settings.gunicorn_bind_port,
        log_config=settings.logging_config,
        log_level=settings.log_level,
    )
