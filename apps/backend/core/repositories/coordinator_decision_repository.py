from __future__ import annotations
from datetime import date
from uuid import UUID
from sqlalchemy import select, func
from infrastructure.database.models import CoordinatorDecision
from core.repositories.base import BaseRepository


class CoordinatorDecisionRepository(BaseRepository[CoordinatorDecision]):
    model = CoordinatorDecision

    async def get_today(self, member_id: UUID, family_id: UUID, decision_date: date) -> CoordinatorDecision | None:
        result = await self._db.execute(
            select(CoordinatorDecision)
            .where(
                CoordinatorDecision.member_id == member_id,
                CoordinatorDecision.family_id == family_id,
                CoordinatorDecision.decision_date == decision_date,
            )
            .order_by(CoordinatorDecision.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def count_today(self, member_id: UUID, family_id: UUID, decision_date: date) -> int:
        result = await self._db.execute(
            select(func.count(CoordinatorDecision.id)).where(
                CoordinatorDecision.member_id == member_id,
                CoordinatorDecision.family_id == family_id,
                CoordinatorDecision.decision_date == decision_date,
            )
        )
        return result.scalar_one() or 0
