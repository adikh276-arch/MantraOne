from __future__ import annotations
from datetime import date
from uuid import UUID
from sqlalchemy import select, func
from infrastructure.database.models import DailyCheckin
from core.repositories.base import BaseRepository

class CheckinRepository(BaseRepository[DailyCheckin]):
    model = DailyCheckin

    async def get_today(self, member_id: UUID, family_id: UUID, checkin_date: date, domain: str) -> DailyCheckin | None:
        result = await self._db.execute(
            select(DailyCheckin).where(
                DailyCheckin.member_id == member_id,
                DailyCheckin.family_id == family_id,
                DailyCheckin.checkin_date == checkin_date,
                DailyCheckin.domain == domain,
            )
        )
        return result.scalar_one_or_none()

    async def count_today(self, member_id: UUID, family_id: UUID, checkin_date: date) -> int:
        result = await self._db.execute(
            select(func.count(DailyCheckin.id)).where(
                DailyCheckin.member_id == member_id,
                DailyCheckin.family_id == family_id,
                DailyCheckin.checkin_date == checkin_date,
            )
        )
        return result.scalar_one() or 0

    async def list_recent(self, member_id: UUID, family_id: UUID, limit: int = 30) -> list[DailyCheckin]:
        result = await self._db.execute(
            select(DailyCheckin).where(
                DailyCheckin.member_id == member_id,
                DailyCheckin.family_id == family_id,
            ).order_by(DailyCheckin.checkin_date.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending_memory_ingestion(self, family_id: UUID, limit: int = 50) -> list[DailyCheckin]:
        result = await self._db.execute(
            select(DailyCheckin).where(
                DailyCheckin.family_id == family_id,
                DailyCheckin.memory_ingested.is_(False),
            ).order_by(DailyCheckin.created_at).limit(limit)
        )
        return list(result.scalars().all())
