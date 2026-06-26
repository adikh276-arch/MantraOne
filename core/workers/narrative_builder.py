from __future__ import annotations
import structlog
from uuid import UUID

logger = structlog.get_logger()

class NarrativeBuilderWorker:
    async def process_event(self, event) -> None:
        logger.info("narrative_builder_process", event_type=event.event_type.value)
        # Generate narrative using NarrativeService, then trigger MemoryProvider
