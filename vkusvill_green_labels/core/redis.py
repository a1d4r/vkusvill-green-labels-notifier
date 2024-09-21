from collections.abc import AsyncIterable

from redis.asyncio import Redis

from vkusvill_green_labels.core.settings import settings

redis = Redis(host=settings.redis.host, port=settings.redis.port)


async def get_redis() -> AsyncIterable[Redis]:
    await redis.initialize()
    yield redis
    await redis.close()
