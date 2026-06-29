from __future__ import annotations
from datetime import datetime
from uuid import UUID
from sqlalchemy import select
from infrastructure.database.models import HealthMetric, Medication, MedicationLog, Diagnosis
from core.repositories.base import BaseRepository


class HealthMetricRepository(BaseRepository[HealthMetric]):
    model = HealthMetric

    async def list_by_type(
        self,
        member_id: UUID,
        family_id: UUID,
        metric_type: str,
        limit: int = 50,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[HealthMetric]:
        conditions = [
            HealthMetric.member_id == member_id,
            HealthMetric.family_id == family_id,
            HealthMetric.metric_type == metric_type,
            HealthMetric.deleted_at.is_(None),
        ]
        if start_date:
            conditions.append(HealthMetric.recorded_at >= start_date)
        if end_date:
            conditions.append(HealthMetric.recorded_at <= end_date)
        result = await self._db.execute(
            select(HealthMetric).where(*conditions).order_by(HealthMetric.recorded_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def list_recent(
        self, member_id: UUID, family_id: UUID, metric_types: list[str], limit: int = 100
    ) -> list[HealthMetric]:
        result = await self._db.execute(
            select(HealthMetric)
            .where(
                HealthMetric.member_id == member_id,
                HealthMetric.family_id == family_id,
                HealthMetric.metric_type.in_(metric_types),
                HealthMetric.deleted_at.is_(None),
            )
            .order_by(HealthMetric.recorded_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


class MedicationRepository(BaseRepository[Medication]):
    model = Medication

    async def list_active(self, member_id: UUID, family_id: UUID) -> list[Medication]:
        result = await self._db.execute(
            select(Medication).where(
                Medication.member_id == member_id,
                Medication.family_id == family_id,
                Medication.is_active.is_(True),
                Medication.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())


class MedicationLogRepository(BaseRepository[MedicationLog]):
    model = MedicationLog

    async def list_recent(self, member_id: UUID, family_id: UUID, days: int = 30) -> list[MedicationLog]:
        from datetime import timedelta, timezone

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self._db.execute(
            select(MedicationLog)
            .where(
                MedicationLog.member_id == member_id,
                MedicationLog.family_id == family_id,
                MedicationLog.scheduled_time >= cutoff,
            )
            .order_by(MedicationLog.scheduled_time.desc())
        )
        return list(result.scalars().all())


class DiagnosisRepository(BaseRepository[Diagnosis]):
    model = Diagnosis

    async def list_active(self, member_id: UUID, family_id: UUID) -> list[Diagnosis]:
        result = await self._db.execute(
            select(Diagnosis).where(
                Diagnosis.member_id == member_id,
                Diagnosis.family_id == family_id,
                Diagnosis.status == "active",
                Diagnosis.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())
