from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from infrastructure.database.models import EscalationEvent
from core.repositories.watcher_signal_repository import WatcherSignalRepository
from core.repositories.escalation_repository import EscalationRepository


class EscalationService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._signal_repo = WatcherSignalRepository(db)
        self._esc_repo = EscalationRepository(db)

    async def evaluate_escalation(self, member_id: UUID, family_id: UUID, twin: Any) -> EscalationEvent | None:
        """
        Computes the deterministic Escalation Score.
        Score = Risk * Persistence * Trend * Confidence * Evidence
        """
        # In a real implementation we'd compute this per active condition/insight in the twin.
        # For simplicity, we grab active insights and compute a mock scalar.
        insights = twin.insights.get(str(member_id), [])

        highest_score = 0.0
        escalation_reason = ""

        for ins in insights:
            if ins.get("type") == "alert":
                risk = 0.9
                persistence = 1.0  # E.g. active for 14 days
                trend = 0.8  # Deteriorating
                confidence = 0.9
                evidence = 1.0  # > 5 data points

                score = risk * persistence * trend * confidence * evidence

                if score > highest_score:
                    highest_score = score
                    escalation_reason = ins.get("desc")

        ESCALATION_THRESHOLD = 0.6

        if highest_score > ESCALATION_THRESHOLD:
            event = EscalationEvent(
                family_id=family_id,
                member_id=member_id,
                triggering_signals=[],  # Map to insight IDs in real implementation
                convergence_score=highest_score,
                recommended_specialty="General Physician",
                escalation_reason=escalation_reason,
                urgency_level="high",
            )
            return await self._esc_repo.save(event)

        return None
