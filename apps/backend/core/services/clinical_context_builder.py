from uuid import UUID
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.domain.entities import ClinicalContext, MemoryFragment
from infrastructure.database.models import DomainConfidence, FollowUp, HealthInsight, FamilyMember
from core.providers.memory_provider import MemoryProvider
from core.services.confidence_calculator import ConfidenceCalculator


class ClinicalContextBuilder:
    """
    Constructs the canonical clinical context package for LLM interactions.
    Never dumps raw memories directly into the prompt.
    """

    def __init__(self, db: AsyncSession):
        self._db = db
        self._memory_provider = MemoryProvider()
        self._confidence_calc = ConfidenceCalculator()

    async def build_context(self, member_id: UUID, family_id: UUID, query: str = "") -> ClinicalContext:
        context = ClinicalContext()

        # 1. Family Member Summary
        res_member = await self._db.execute(select(FamilyMember).where(FamilyMember.id == member_id))
        member = res_member.scalar_one_or_none()
        if member:
            context.patient_summary = {
                "name": member.name,
                "relationship": member.relationship,
                "role": member.role,
                "dob": member.date_of_birth,
                "gender": member.gender,
            }

        # 2. Domain Confidence (and missing information)
        res_conf = await self._db.execute(select(DomainConfidence).where(DomainConfidence.member_id == member_id))
        confidences = res_conf.scalars().all()
        for conf in confidences:
            freshness = self._confidence_calc.calculate_current_freshness(conf, "default")
            context.confidence[conf.domain] = {
                "completeness": conf.completeness,
                "freshness": freshness,
                "confidence": conf.confidence,
            }
            if freshness < 0.3:
                context.missing_information.append(f"Outdated information for {conf.domain}")
            if conf.completeness < 0.5:
                context.missing_information.append(f"Incomplete information for {conf.domain}")

        # 3. Active Insights (Recent changes, Active conditions)
        res_insights = await self._db.execute(
            select(HealthInsight).where(
                HealthInsight.member_id == member_id, HealthInsight.status.in_(["active", "updated", "generated"])
            )
        )
        insights = res_insights.scalars().all()
        for insight in insights:
            if insight.insight_type == "alert":
                context.recent_changes.append(insight.description)
            elif insight.insight_type == "trend":
                context.timeline_summary.append(
                    {"date": insight.created_at.isoformat(), "description": insight.description}
                )
            elif insight.insight_type == "gap":
                context.missing_information.append(insight.description)

            # If structured data contains specific fields, map them
            if insight.structured_data:
                context.active_conditions.extend(insight.structured_data.get("worsening_conditions", []))
                context.active_conditions.extend(insight.structured_data.get("improving_conditions", []))

        # 4. Pending Follow-ups
        res_followups = await self._db.execute(
            select(FollowUp).where(
                FollowUp.member_id == member_id, FollowUp.status.in_(["scheduled", "pending", "overdue"])
            )
        )
        followups = res_followups.scalars().all()
        for fu in followups:
            context.pending_followups.append(
                {
                    "description": fu.description,
                    "due_date": fu.due_date.isoformat() if fu.due_date else None,
                    "status": fu.status,
                }
            )

        # 5. Retrieved Memories (only relevant to the specific query if provided)
        if query:
            fragments = await self._memory_provider.recall(query, family_id, member_id, limit=5)
            context.retrieved_memories = fragments

        return context
