from redis import asyncio as aioredis

redis: aioredis.Redis | None = None


async def get_aioredis() -> aioredis.Redis:
    return redis
