from http import HTTPStatus

import uvicorn
from api.v1.api import api_router as api_router_v1
from core.config import jwt_settings, settings
from db import elastic, redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, FastAPI, Request
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from redis import Redis
from redis import asyncio as aioredis
from services.jwt_auth import auth_service

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    dependencies=[Depends(auth_service)],
)


@AuthJWT.load_config
def get_config():
    return jwt_settings


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return ORJSONResponse(
        status_code=exc.status_code, content={"detail": exc.message}
    )


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token["jti"]
    print(jti)
    entry = redis.jwt_denylist.get(jti)
    print(entry)
    return entry is not None


app.include_router(api_router_v1, prefix=settings.api_v1_base_path)


@app.on_event("startup")
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

    redis.jwt_denylist = Redis.from_url(
        jwt_settings.redis_denylist_dsn,
        max_connections=10,
        encoding="utf8",
        decode_responses=True,
    )


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


@app.exception_handler(NotFoundError)
async def es_not_found_exception_handler(exc: NotFoundError):
    return ORJSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={
            "message": f"Index not found. If you're testing, "
            f"you should create or restore indexes first.\n{exc}"
        },
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.gunicorn_host,
        port=settings.gunicorn_port,
        log_config=settings.logging_config,
        log_level=settings.log_level,
    )
