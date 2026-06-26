from __future__ import annotations
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy import select, update
from infrastructure.database.models import WatcherSignal, HealthBaseline
from core.repositories.base import BaseRepository

class WatcherSignalRepository(BaseRepository[WatcherSignal]):
    model = WatcherSignal

    async def list_unsurfaced(self, family_id: UUID, member_id: UUID, lookback_hours: int = 48) -> list[WatcherSignal]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
        result = await self._db.execute(
            select(WatcherSignal).where(
                WatcherSignal.family_id == family_id,
                WatcherSignal.member_id == member_id,
                WatcherSignal.surfaced.is_(False),
                WatcherSignal.created_at >= cutoff,
            ).order_by(WatcherSignal.created_at.desc())
        )
        return list(result.scalars().all())

    async def mark_surfaced(self, signal_ids: list[UUID], family_id: UUID) -> None:
        await self._db.execute(
            update(WatcherSignal)
            .where(WatcherSignal.id.in_(signal_ids), WatcherSignal.family_id == family_id)
            .values(surfaced=True, surfaced_at=datetime.now(timezone.utc))
        )

    async def list_by_domain(self, member_id: UUID, family_id: UUID, domain: str, days: int = 7) -> list[WatcherSignal]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self._db.execute(
            select(WatcherSignal).where(
                WatcherSignal.member_id == member_id,
                WatcherSignal.family_id == family_id,
                WatcherSignal.watcher_domain == domain,
                WatcherSignal.created_at >= cutoff,
            ).order_by(WatcherSignal.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_recent_all_domains(self, member_id: UUID, family_id: UUID, days: int = 7) -> list[WatcherSignal]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self._db.execute(
            select(WatcherSignal).where(
                WatcherSignal.member_id == member_id,
                WatcherSignal.family_id == family_id,
                WatcherSignal.created_at >= cutoff,
            ).order_by(WatcherSignal.created_at.desc())
        )
        return list(result.scalars().all())

class HealthBaselineRepository(BaseRepository[HealthBaseline]):
    model = HealthBaseline

    async def get_for_domain(self, member_id: UUID, family_id: UUID, domain: str) -> HealthBaseline | None:
        result = await self._db.execute(
            select(HealthBaseline).where(
                HealthBaseline.member_id == member_id,
                HealthBaseline.family_id == family_id,
                HealthBaseline.domain == domain,
            )
        )
        return result.scalar_one_or_none()

    async def upsert(self, family_id: UUID, member_id: UUID, domain: str, baseline_data_encrypted: str, data_points_count: int, confidence_score: float) -> HealthBaseline:
        existing = await self.get_for_domain(member_id, family_id, domain)
        if existing:
            existing.baseline_data = baseline_data_encrypted
            existing.data_points_count = data_points_count
            existing.confidence_score = confidence_score
            existing.calculated_at = datetime.now(timezone.utc)
            return await self.save(existing)
        baseline = HealthBaseline(
            family_id=family_id, member_id=member_id, domain=domain,
            baseline_data=baseline_data_encrypted, data_points_count=data_points_count,
            confidence_score=confidence_score,
        )
        return await self.save(baseline)
