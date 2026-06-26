from __future__ import annotations
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import HealthMetric, Medication, MedicationLog
from core.repositories.health_record_repository import HealthMetricRepository, MedicationRepository, MedicationLogRepository
from core.providers.encryption_service import EncryptionService

class HealthRecordService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._metric_repo = HealthMetricRepository(db)
        self._med_repo = MedicationRepository(db)
        self._log_repo = MedicationLogRepository(db)
        self._enc = EncryptionService()

    async def record_metric(self, member_id: UUID, family_id: UUID, metric_type: str, recorded_at: datetime, value_numeric: float | None = None, value_systolic: float | None = None, value_diastolic: float | None = None, unit: str | None = None, notes: str | None = None) -> HealthMetric:
        metric = HealthMetric(
            family_id=family_id,
            member_id=member_id,
            metric_type=metric_type,
            recorded_at=recorded_at,
            value_numeric=value_numeric,
            value_systolic=value_systolic,
            value_diastolic=value_diastolic,
            unit=unit,
            notes=self._enc.encrypt_optional(notes),
        )
        return await self._metric_repo.save(metric)

    async def add_medication(self, member_id: UUID, family_id: UUID, name: str, start_date: datetime.date, dosage: str | None = None, frequency: str | None = None) -> Medication:
        med = Medication(
            family_id=family_id,
            member_id=member_id,
            name=self._enc.encrypt(name),
            start_date=start_date,
            dosage=self._enc.encrypt_optional(dosage),
            frequency=self._enc.encrypt_optional(frequency),
        )
        return await self._med_repo.save(med)

    async def log_medication(self, medication_id: UUID, member_id: UUID, family_id: UUID, status: str, scheduled_time: datetime, taken_at: datetime | None = None, notes: str | None = None) -> MedicationLog:
        log = MedicationLog(
            family_id=family_id,
            member_id=member_id,
            medication_id=medication_id,
            scheduled_time=scheduled_time,
            status=status,
            taken_at=taken_at,
            notes=self._enc.encrypt_optional(notes),
        )
        return await self._log_repo.save(log)
