from __future__ import annotations
from uuid import UUID
from core.domain.entities import MemoryFragment, HealthContext
from core.domain.enums import WatcherDomain
from core.providers.memory_provider import MemoryProvider
from core.domain.entities import WatcherSignalEntity
import structlog

logger = structlog.get_logger()

class RetrievalService:
    def __init__(self, memory_provider: MemoryProvider) -> None:
        self._memory = memory_provider

    async def recall_domain_context(self, member_id: UUID, family_id: UUID, domain: WatcherDomain, lookback_days: int = 30) -> list[MemoryFragment]:
        query = f"{domain.value} health patterns and trends over {lookback_days} days"
        return await self._memory.recall(query=query, family_id=family_id, member_id=member_id, limit=10)

    async def recall_for_checkin(self, member_id: UUID, family_id: UUID, domain: WatcherDomain, recent_signals: list[WatcherSignalEntity]) -> str:
        fragments = await self.recall_domain_context(member_id, family_id, domain, 14)
        context_parts = [f.content[:300] for f in fragments[:5]]
        signal_context = "; ".join(f"{s.watcher_domain.value}: {s.trend_direction.value if s.trend_direction else 'notable'}" for s in recent_signals[:3])
        return f"Recent memory: {' | '.join(context_parts[:3])}. Signals: {signal_context}"

    async def build_doctor_brief_context(self, member_id: UUID, family_id: UUID, triggering_domains: list[WatcherDomain], lookback_days: int = 90) -> HealthContext:
        domain_names = [d.value for d in triggering_domains]
        return await self._memory.get_health_context(member_id=member_id, family_id=family_id, include_domains=domain_names, lookback_days=lookback_days)

    async def search_by_query(self, query: str, member_id: UUID, family_id: UUID, limit: int = 10) -> list[MemoryFragment]:
        return await self._memory.recall(query=query, family_id=family_id, member_id=member_id, limit=limit)
