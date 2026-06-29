from redis.asyncio import Redis, ConnectionPool
from config.settings import settings
import structlog

logger = structlog.get_logger()
_pool: ConnectionPool | None = None


def get_redis_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool.from_url(
            settings.redis_url,
            max_connections=settings.redis_max_connections,
            decode_responses=True,
        )
    return _pool


async def get_redis_client() -> Redis:
    return Redis(connection_pool=get_redis_pool())


async def close_redis_pool() -> None:
    global _pool
    if _pool:
        await _pool.disconnect()
        _pool = None


STREAM_NAME = "mantraone:health_events"


async def create_consumer_group(redis: Redis, stream: str, group: str) -> None:
    try:
        await redis.xgroup_create(stream, group, id="0", mkstream=True)
    except Exception as e:
        if "BUSYGROUP" not in str(e):
            raise


async def publish_event(
    redis: Redis, event_type: str, event_id: str, idempotency_key: str, data: str, timestamp: str
) -> str:
    entry_id = await redis.xadd(
        STREAM_NAME,
        {
            "event_type": event_type,
            "event_id": event_id,
            "idempotency_key": idempotency_key,
            "timestamp": timestamp,
            "data": data,
        },
        maxlen=100_000,
        approximate=True,
    )
    logger.info("redis_stream_published", event_type=event_type, stream=STREAM_NAME, entry_id=entry_id)
    return entry_id
