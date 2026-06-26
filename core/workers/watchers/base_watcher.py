from __future__ import annotations
import structlog
from typing import Any
from core.domain.enums import WatcherDomain
from core.events.types import BaseHealthEvent

logger = structlog.get_logger()

class BaseWatcher:
    domain: WatcherDomain

    async def evaluate(self, member_id: str, family_id: str, events: list[BaseHealthEvent]) -> None:
        logger.info("watcher_evaluating", domain=self.domain.value, member_id=member_id)
        await self._process(member_id, family_id, events)

    async def _process(self, member_id: str, family_id: str, events: list[BaseHealthEvent]) -> None:
        raise NotImplementedError
