from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import EscalationEvent
from core.repositories.watcher_signal_repository import WatcherSignalRepository
from core.repositories.escalation_repository import EscalationRepository
from core.providers.llm_provider import LLMProvider

class EscalationService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._signal_repo = WatcherSignalRepository(db)
        self._esc_repo = EscalationRepository(db)
        self._llm = LLMProvider()

    async def evaluate_escalation(self, member_id: UUID, family_id: UUID) -> EscalationEvent | None:
        # Mock logic for escalation evaluation
        recent_signals = await self._signal_repo.list_recent_all_domains(member_id, family_id)
        if len(recent_signals) < 2:
            return None
            
        reason = await self._llm.generate_escalation_reason(
            domains=[s.watcher_domain for s in recent_signals],
            signals=[{"domain": s.watcher_domain} for s in recent_signals],
            member_context="Member context"
        )
        
        event = EscalationEvent(
            family_id=family_id,
            member_id=member_id,
            triggering_signals=[{"signal_id": str(s.id)} for s in recent_signals],
            convergence_score=0.8,
            recommended_specialty="General Physician",
            escalation_reason=reason,
            urgency_level="soon",
        )
        return await self._esc_repo.save(event)
