from abc import ABC, abstractmethod
from uuid import UUID
from datetime import datetime
from core.domain.entities import HealthMemoryMetadata, MemoryFragment, HealthContext, ForgetResult

class IMemoryProvider(ABC):
    @abstractmethod
    async def remember(self, content: str, metadata: HealthMemoryMetadata) -> str: pass
    @abstractmethod
    async def recall(self, query: str, family_id: UUID, member_id: UUID, limit: int = 10, min_confidence: float = 0.5) -> list[MemoryFragment]: pass
    @abstractmethod
    async def get_health_context(self, member_id: UUID, include_domains: list[str], lookback_days: int = 30, family_id: UUID | None = None) -> HealthContext: pass
    @abstractmethod
    async def forget(self, family_id: UUID, member_id: UUID | None = None, before_date: datetime | None = None) -> ForgetResult: pass
