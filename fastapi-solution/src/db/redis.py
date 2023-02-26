from redis import Redis
from redis import asyncio as aioredis

redis: aioredis.Redis | None = None
jwt_denylist: Redis | None = None


async def get_aioredis() -> aioredis.Redis:
    return redis


def get_jwtblacklist() -> aioredis.Redis:
    return jwt_denylist
