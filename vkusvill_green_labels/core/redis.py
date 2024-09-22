from collections.abc import AsyncIterable

from redis.asyncio import Redis

from vkusvill_green_labels.core.settings import settings

redis = Redis.from_url(url=str(settings.redis.dsn))


async def get_redis() -> AsyncIterable[Redis]:
    await redis.initialize()
    yield redis
    await redis.close()
