from pyrate_limiter import Limiter
from pyrate_limiter.buckets.redis_bucket import RedisBucket
from redis.asyncio import Redis

from vkusvill_green_labels.core.settings import settings


async def get_redis_bucket(redis: Redis) -> RedisBucket:
    return await RedisBucket.init(  # type: ignore[no-any-return]
        rates=settings.rate_limits.rates, redis=redis, bucket_key="rate-limits"
    )


def provide_rate_limiter(redis_bucket: RedisBucket) -> Limiter:
    return Limiter(redis_bucket, raise_when_fail=False, max_delay=settings.rate_limits.max_delay_ms)
