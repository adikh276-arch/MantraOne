from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from infrastructure.database.models import KnowledgeGap, NextAction
from core.domain.entities import FamilyDigitalTwin
from core.services.knowledge_gap_service import KnowledgeGapService
from core.services.user_fatigue_service import UserFatigueService
from core.services.information_gain_service import InformationGainService
from core.services.adaptive_interview_service import AdaptiveInterviewService


class DecisionEngine:
    """
    The master orchestrator of the Adaptive Intelligence Loop.
    Answers: "What is the single highest-value action I can take?"
    """

    def __init__(self, db: AsyncSession):
        self._db = db
        self._gap_service = KnowledgeGapService(db)
        self._fatigue_service = UserFatigueService(db)
        self._info_service = InformationGainService()
        self._interview_service = AdaptiveInterviewService()

    async def determine_next_action(self, twin: FamilyDigitalTwin, member_id: UUID) -> NextAction:
        """
        Calculates the single best action to take for the member based on the Digital Twin.
        """
        # 1. Detect Gaps
        gaps = await self._gap_service.identify_gaps(twin, member_id)

        # 2. Check Fatigue
        fatigue_multiplier = await self._fatigue_service.get_fatigue_multiplier(member_id)

        # 3. Score all possible actions
        best_gap = None
        highest_score = 0.0

        for gap in gaps:
            score = self._info_service.score_gap(gap, fatigue_multiplier)
            if score > highest_score:
                highest_score = score
                best_gap = gap

        # 4. Thresholding for ACTION vs WAIT
        ACTION_THRESHOLD = 0.5

        if not best_gap or highest_score < ACTION_THRESHOLD:
            # Not worth interrupting the user, or no gaps
            action = NextAction(
                family_id=twin.family_id,
                member_id=member_id,
                action_type="WAIT",
                priority=highest_score,
                reason="No high-value knowledge gaps exceed the fatigue threshold.",
                status="pending",
            )
            self._db.add(action)
            await self._db.commit()
            return action

        # 5. We decided to act. Generate the specific action.
        if best_gap.suggested_action == "ASK_QUESTION":
            # Generate the adaptive interview question
            context_vars = {"medication": "medication", "lab_type": "lab", "symptom": "symptom"}
            # In real app, extract specific entity from the reason
            if "adherence" in best_gap.domain:
                q = self._interview_service.generate_question("medication_adherence", context_vars)
            elif "lab" in best_gap.domain:
                q = self._interview_service.generate_question("missing_lab", context_vars)
            elif "progression" in best_gap.domain:
                q = self._interview_service.generate_question("symptom_progression", context_vars)
            else:
                q = self._interview_service.generate_question("unknown", context_vars)

            action = NextAction(
                family_id=twin.family_id,
                member_id=member_id,
                action_type="ASK_QUESTION",
                priority=highest_score,
                reason=f"High-priority information gain regarding {best_gap.domain}.",
                execution_strategy=q,
                status="pending",
            )

            # Record that we are asking a question to update fatigue
            await self._fatigue_service.record_interaction(member_id, "asked")

        elif best_gap.suggested_action == "REQUEST_REPORT":
            action = NextAction(
                family_id=twin.family_id,
                member_id=member_id,
                action_type="REQUEST_REPORT",
                priority=highest_score,
                reason=best_gap.reason,
                status="pending",
            )
            await self._fatigue_service.record_interaction(member_id, "asked")
        else:
            action = NextAction(
                family_id=twin.family_id,
                member_id=member_id,
                action_type="WAIT",
                priority=0.0,
                reason="Fallback. Unknown action type.",
                status="pending",
            )

        self._db.add(action)
        await self._db.commit()

        return action
