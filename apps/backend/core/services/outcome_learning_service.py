from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from infrastructure.database.models import ClinicalOutcome
from core.providers.memory_provider import MemoryProvider


class OutcomeLearningService:
    """
    Ingests outcomes from clinical consultations and feeds them back into the system
    as high-confidence ground truth memories.
    """

    def __init__(self, db: AsyncSession):
        self._db = db
        self._memory = MemoryProvider()

    async def ingest_outcome(
        self, family_id: UUID, member_id: UUID, diagnosis: str, treatment_plan: str, notes: str
    ) -> ClinicalOutcome:
        """
        Stores the clinical outcome and immediately updates the semantic memory with high confidence.
        """
        outcome = ClinicalOutcome(
            family_id=family_id,
            member_id=member_id,
            diagnosis=diagnosis,
            treatment_plan=treatment_plan,
            doctor_notes=notes,
            resolved_status=True,
        )
        self._db.add(outcome)
        await self._db.commit()

        # Inject as a high confidence memory
        memory_content = f"CLINICAL OUTCOME - Diagnosis: {diagnosis}. Treatment Plan: {treatment_plan}. Notes: {notes}."

        await self._memory.remember(
            content=memory_content,
            metadata={
                "family_id": family_id,
                "member_id": member_id,
                "memory_type": "clinical_outcome",
                "confidence": 1.0,  # Ground truth
                "outcome_id": str(outcome.id),
            },
        )

        return outcome
