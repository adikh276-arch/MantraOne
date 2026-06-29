from abc import ABC, abstractmethod
from core.events.types import BaseHealthEvent


class IEventPublisher(ABC):
    @abstractmethod
    async def publish(self, event: BaseHealthEvent) -> str:
        pass

    @abstractmethod
    async def publish_many(self, events: list[BaseHealthEvent]) -> list[str]:
        pass
