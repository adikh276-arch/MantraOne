from __future__ import annotations
import asyncio
from arq import worker
from config.settings import settings
import structlog
from redis.asyncio import Redis
from infrastructure.cache.redis_client import get_redis_pool
from core.events.subscriber import EventSubscriber

logger = structlog.get_logger()


async def startup(ctx: dict) -> None:
    logger.info("worker_startup")
    pool = get_redis_pool()
    ctx["redis"] = Redis(connection_pool=pool)
    sub = EventSubscriber(ctx["redis"])
    sub.group_name = "mantraone_workers"
    sub.consumer_name = "arq_worker_1"
    await sub.ensure_consumer_group()
    ctx["subscriber"] = sub
    logger.info("worker_ready")


async def shutdown(ctx: dict) -> None:
    logger.info("worker_shutdown")
    if "redis" in ctx:
        await ctx["redis"].close()


async def process_events_loop(ctx: dict) -> None:
    sub: EventSubscriber = ctx["subscriber"]
    logger.info("event_loop_started")
    while True:
        try:
            events = await sub.poll_events(count=10, block_ms=2000)
            for entry_id, event in events:
                logger.info("processing_event", event_type=event.event_type.value, event_id=str(event.event_id))
                # Event Router logic would go here to dispatch to watchers/workers
                await sub.acknowledge(entry_id)
        except Exception as exc:
            logger.error("event_loop_error", error=str(exc))
            await asyncio.sleep(1)


class WorkerSettings:
    redis_settings = worker.RedisSettings(host=settings.redis_url.split("://")[1].split(":")[0], port=6379)
    on_startup = startup
    on_shutdown = shutdown
    functions = [process_events_loop]
