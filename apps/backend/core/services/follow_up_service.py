from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.services.clinical_rules_engine import ClinicalRulesEngine
from infrastructure.database.models import FollowUp
from core.providers.llm_provider import LLMProvider
import structlog

logger = structlog.get_logger()


class FollowUpService:
    """
    Manages the lifecycle of clinical follow-ups.
    Uses deterministic rules for timing, and optional LLM for personalization.
    """

    def __init__(self, db: AsyncSession):
        self._db = db
        self._rules_engine = ClinicalRulesEngine()
        self._llm = LLMProvider()

    async def schedule_follow_ups(self, member_id: UUID, family_id: UUID, entities: List[dict]) -> None:
        """
        Scans a list of newly extracted medical entities (e.g. from DocumentIntelligenceService)
        and deterministically schedules follow-ups.

        entities format: [{"name": "Diabetes", "type": "diagnosis"}, ...]
        """
        new_followups = []
        now = datetime.now(timezone.utc)

        for entity in entities:
            entity_name = entity.get("name")
            entity_type = entity.get("type")
            if not entity_name or not entity_type:
                continue

            due_date = self._rules_engine.calculate_due_date(entity_name, entity_type, base_date=now)
            if due_date:
                # Optional LLM Personalization for the description
                # In a robust setup we'd prompt the LLM to rewrite the reminder.
                # For efficiency we'll just use a standard template.
                description = f"Follow-up required for {entity_type}: {entity_name}"

                fu = FollowUp(
                    family_id=family_id,
                    member_id=member_id,
                    description=description,
                    due_date=due_date,
                    status="scheduled",
                )
                new_followups.append(fu)

        if new_followups:
            self._db.add_all(new_followups)
            await self._db.commit()
            logger.info("follow_ups_scheduled", count=len(new_followups), member_id=str(member_id))

    async def transition_follow_up(self, follow_up_id: UUID, new_status: str) -> Optional[FollowUp]:
        """
        Transitions a follow-up through its lifecycle:
        Scheduled -> Pending -> Completed -> Dismissed -> Overdue -> Escalated
        """
        res = await self._db.execute(select(FollowUp).where(FollowUp.id == follow_up_id))
        fu = res.scalar_one_or_none()
        if fu:
            fu.status = new_status
            await self._db.commit()
            await self._db.refresh(fu)
        return fu
