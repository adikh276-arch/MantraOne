from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import CoordinatorDecision
from core.repositories.watcher_signal_repository import WatcherSignalRepository
from core.repositories.coordinator_decision_repository import CoordinatorDecisionRepository
from core.providers.llm_provider import LLMProvider

class CoordinatorService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._signal_repo = WatcherSignalRepository(db)
        self._decision_repo = CoordinatorDecisionRepository(db)
        self._llm = LLMProvider()

    async def select_daily_signal(self, member_id: UUID, family_id: UUID) -> CoordinatorDecision | None:
        # Pseudo-implementation matching the plan
                
        # In a full implementation, we'd rank signals and pick the top one.
        # For now, just generate a record.
        signals = await self._signal_repo.list_unsurfaced(family_id, member_id)
        if not signals:
            return None
            
        top_signal = signals[0]
        
        question = await self._llm.generate_checkin_question(
            domain=top_signal.watcher_domain,
            member_name="Member",
            context="Past memory context",
            recent_signals=[{"domain": top_signal.watcher_domain, "trend_direction": "declining"}]
        )
        
        decision = CoordinatorDecision(
            family_id=family_id,
            member_id=member_id,
            selected_domain=top_signal.watcher_domain,
            selection_reason="urgency",
            selected_signal_ids=[top_signal.id],
            checkin_generated=question,
        )
        saved = await self._decision_repo.save(decision)
        
        await self._signal_repo.mark_surfaced([top_signal.id], family_id)
        
        return saved
