from __future__ import annotations
import json
from typing import Any
from redis.asyncio import Redis
from core.events.types import BaseHealthEvent, EVENT_TYPE_MAP
from core.domain.enums import HealthEventType
from infrastructure.cache.redis_client import STREAM_NAME, create_consumer_group
import structlog

logger = structlog.get_logger()

class EventSubscriber:
    group_name: str = ""
    consumer_name: str = ""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def ensure_consumer_group(self) -> None:
        await create_consumer_group(self._redis, STREAM_NAME, self.group_name)

    async def poll_events(
        self,
        event_types: list[HealthEventType] | None = None,
        count: int = 10,
        block_ms: int = 1000,
    ) -> list[tuple[str, BaseHealthEvent]]:
        raw: list[Any] = await self._redis.xreadgroup(
            groupname=self.group_name,
            consumername=self.consumer_name,
            streams={STREAM_NAME: ">"},
            count=count,
            block=block_ms,
        )

        results: list[tuple[str, BaseHealthEvent]] = []
        if not raw:
            return results

        for _stream, entries in raw:
            for entry_id, fields in entries:
                event_type_str = fields.get("event_type", "")
                try:
                    event_type = HealthEventType(event_type_str)
                except ValueError:
                    logger.warning("unknown_event_type", event_type=event_type_str)
                    await self.acknowledge(entry_id)
                    continue

                if event_types and event_type not in event_types:
                    await self.acknowledge(entry_id)
                    continue

                event_class = EVENT_TYPE_MAP.get(event_type)
                if not event_class:
                    logger.warning("no_handler_for_event_type", event_type=event_type_str)
                    await self.acknowledge(entry_id)
                    continue

                try:
                    data = json.loads(fields["data"])
                    event = event_class.model_validate(data)
                    results.append((entry_id, event))
                except Exception as exc:
                    logger.error("event_deserialization_failed", entry_id=entry_id, error=str(exc))
                    await self.acknowledge(entry_id)

        return results

    async def acknowledge(self, entry_id: str) -> None:
        await self._redis.xack(STREAM_NAME, self.group_name, entry_id)

    async def claim_pending(
        self,
        min_idle_ms: int = 30_000,
        count: int = 10,
    ) -> list[tuple[str, BaseHealthEvent]]:
        try:
            claimed = await self._redis.xautoclaim(
                STREAM_NAME,
                self.group_name,
                self.consumer_name,
                min_idle_time=min_idle_ms,
                start_id="0",
                count=count,
            )
            results: list[tuple[str, BaseHealthEvent]] = []
            if not claimed or not claimed[1]:
                return results
            for entry_id, fields in claimed[1]:
                event_type_str = fields.get("event_type", "")
                try:
                    event_type = HealthEventType(event_type_str)
                    event_class = EVENT_TYPE_MAP[event_type]
                    data = json.loads(fields["data"])
                    event = event_class.model_validate(data)
                    results.append((entry_id, event))
                except Exception as exc:
                    logger.error("pending_claim_failed", entry_id=entry_id, error=str(exc))
            return results
        except Exception as exc:
            logger.error("xautoclaim_failed", error=str(exc))
            return []
