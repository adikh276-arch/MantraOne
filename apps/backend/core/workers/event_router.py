from __future__ import annotations
import structlog
from core.events.types import BaseHealthEvent, HealthEventType

logger = structlog.get_logger()


class EventRouter:
    def __init__(self):
        self.routes = {}

    def register(self, event_type: HealthEventType, handler):
        if event_type not in self.routes:
            self.routes[event_type] = []
        self.routes[event_type].append(handler)

    async def dispatch(self, event: BaseHealthEvent):
        handlers = self.routes.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error("handler_error", event_type=event.event_type, handler=handler.__name__, error=str(e))
