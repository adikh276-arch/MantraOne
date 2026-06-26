from __future__ import annotations
import structlog

logger = structlog.get_logger()

class EscalationEngine:
    async def process_signals(self) -> None:
        logger.info("escalation_engine_running")
