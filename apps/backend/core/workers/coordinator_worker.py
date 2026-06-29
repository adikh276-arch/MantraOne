from __future__ import annotations
import structlog

logger = structlog.get_logger()


class CoordinatorWorker:
    async def process_daily_evaluations(self) -> None:
        logger.info("coordinator_evaluating")
