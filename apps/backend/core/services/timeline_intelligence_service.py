from uuid import UUID
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from infrastructure.database.models import HealthInsight
from core.domain.entities import TimelineEvent


class TimelineIntelligenceService:
    """
    Interweaves raw timeline events with structured health insights to provide
    an intelligent, summarized view of a patient's health trajectory.
    """

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_intelligent_timeline(self, member_id: UUID) -> List[Dict]:
        """
        Retrieves raw events (if any are stored in a relational way, e.g., daily checkins)
        and overlays HealthInsights (trends, alerts) to create a chronological story.
        """
        # Fetch timeline-worthy insights (trends and alerts)
        res = await self._db.execute(
            select(HealthInsight)
            .where(HealthInsight.member_id == member_id, HealthInsight.insight_type.in_(["trend", "alert"]))
            .order_by(HealthInsight.created_at.desc())
        )
        insights = res.scalars().all()

        timeline = []
        for insight in insights:
            timeline.append(
                {
                    "date": insight.created_at.isoformat(),
                    "type": insight.insight_type,
                    "title": "Health Alert" if insight.insight_type == "alert" else "Trajectory Trend",
                    "description": insight.description,
                    "status": insight.status,
                }
            )

        # Here we would typically also merge in raw TimelineEvents or checkins,
        # but the insights are the core "intelligent" part.

        return timeline
