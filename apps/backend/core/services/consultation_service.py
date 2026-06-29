from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import Consultation
from core.repositories.escalation_repository import ConsultationRepository


class ConsultationService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = ConsultationRepository(db)

    async def create_consultation(
        self, escalation_id: UUID, family_id: UUID, member_id: UUID, consultation_type: str, specialty: str
    ) -> Consultation:
        consult = Consultation(
            family_id=family_id,
            member_id=member_id,
            escalation_id=escalation_id,
            consultation_type=consultation_type,
            specialty=specialty,
        )
        return await self._repo.save(consult)
