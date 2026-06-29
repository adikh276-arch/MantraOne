from __future__ import annotations
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy import select
from infrastructure.database.models import EscalationEvent, Consultation
from core.repositories.base import BaseRepository


class EscalationRepository(BaseRepository[EscalationEvent]):
    model = EscalationEvent

    async def get_pending_for_member(self, member_id: UUID, family_id: UUID) -> list[EscalationEvent]:
        result = await self._db.execute(
            select(EscalationEvent)
            .where(
                EscalationEvent.member_id == member_id,
                EscalationEvent.family_id == family_id,
                EscalationEvent.status == "pending",
            )
            .order_by(EscalationEvent.triggered_at.desc())
        )
        return list(result.scalars().all())

    async def get_recent(self, member_id: UUID, family_id: UUID, days: int = 7) -> list[EscalationEvent]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self._db.execute(
            select(EscalationEvent)
            .where(
                EscalationEvent.member_id == member_id,
                EscalationEvent.family_id == family_id,
                EscalationEvent.triggered_at >= cutoff,
            )
            .order_by(EscalationEvent.triggered_at.desc())
        )
        return list(result.scalars().all())


class ConsultationRepository(BaseRepository[Consultation]):
    model = Consultation

    async def list_for_member(self, member_id: UUID, family_id: UUID, limit: int = 20) -> list[Consultation]:
        result = await self._db.execute(
            select(Consultation)
            .where(
                Consultation.member_id == member_id,
                Consultation.family_id == family_id,
                Consultation.deleted_at.is_(None),
            )
            .order_by(Consultation.scheduled_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
