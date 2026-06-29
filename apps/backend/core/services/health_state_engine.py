from uuid import UUID
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from infrastructure.database.models import DomainConfidence, HealthInsight


class HealthStateEngine:
    """
    Deterministically computes a Family Member's HealthState based on rules, confidence scores,
    and structured inputs. Never uses an LLM to "invent" a health state.
    """

    def __init__(self, db: AsyncSession):
        self._db = db

    async def compute_state(self, member_id: UUID) -> Dict[str, Any]:
        """
        Computes the deterministic health state for a member.
        Returns a dictionary representing the state.
        """
        # Fetch confidences
        res_conf = await self._db.execute(select(DomainConfidence).where(DomainConfidence.member_id == member_id))
        confidences = res_conf.scalars().all()

        # Fetch active insights (for recent changes and attention needs)
        res_insights = await self._db.execute(
            select(HealthInsight).where(
                HealthInsight.member_id == member_id, HealthInsight.status.in_(["active", "updated"])
            )
        )
        active_insights = res_insights.scalars().all()

        # Deterministic Rules
        # 1. Overall Status
        attention_count = len([i for i in active_insights if i.insight_type in ("alert", "worsening")])
        if attention_count >= 2:
            overall_status = "Attention Needed"
            attention_level = "High"
        elif attention_count == 1:
            overall_status = "Monitoring"
            attention_level = "Moderate"
        else:
            overall_status = "Stable"
            attention_level = "Low"

        # 2. Confidence & Missing Info
        missing_info = []
        overall_confidence_sum = 0.0
        domain_count = 0

        for c in confidences:
            domain_count += 1
            overall_confidence_sum += c.confidence * c.freshness
            if c.freshness < 0.3 or c.completeness < 0.5:
                missing_info.append(f"Needs update for {c.domain}")

        avg_confidence = (overall_confidence_sum / domain_count) if domain_count > 0 else 0.0

        # 3. Recent Changes
        recent_changes = [i.description for i in active_insights if i.insight_type in ("alert", "trend")]

        return {
            "overall_status": overall_status,
            "attention_level": attention_level,
            "confidence_score": round(avg_confidence, 2),
            "recent_changes": recent_changes[:5],  # Top 5
            "missing_information": missing_info,
        }
