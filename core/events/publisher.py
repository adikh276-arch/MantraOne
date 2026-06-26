from __future__ import annotations
from redis.asyncio import Redis
from core.events.types import BaseHealthEvent
from infrastructure.cache.redis_client import publish_event
import structlog
from core.contracts.event import IEventPublisher

logger = structlog.get_logger()

class EventPublisher(IEventPublisher):
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def publish(self, event: BaseHealthEvent) -> str:
        return await publish_event(self._redis, event.event_type.value, str(event.event_id), event.idempotency_key, event.model_dump_json(), event.timestamp.isoformat())

    async def publish_many(self, events: list[BaseHealthEvent]) -> list[str]:
        return []
