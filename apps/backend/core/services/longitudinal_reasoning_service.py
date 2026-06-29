from uuid import UUID
from datetime import datetime, timezone, timedelta
from typing import List, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from infrastructure.database.models import HealthInsight, DomainConfidence
from core.providers.llm_provider import LLMProvider
from pydantic import BaseModel, Field
import json


class LongitudinalObservationSchema(BaseModel):
    trends: List[str] = Field(description="Structured trends over the period.")
    medication_effectiveness: List[str] = Field(description="Observations on medication efficacy.")
    disease_progression: List[str] = Field(description="Observations on disease progression.")
    new_risks: List[str] = Field(description="Newly identified risks.")
    improvements: List[str] = Field(description="Areas showing improvement.")
    regressions: List[str] = Field(description="Areas showing regression.")


class LongitudinalReasoningService:
    """
    Reasons across time (30/90/365 days).
    Outputs structured observations, NEVER prose.
    """

    SYSTEM_PROMPT = """You are a clinical reasoning engine. 
    Analyze the health timeline provided and output strictly structured JSON matching the requested schema.
    Focus on trends, effectiveness, progression, and regressions over the specified time window.
    """

    def __init__(self, db: AsyncSession):
        self._db = db
        self._llm = LLMProvider()

    async def analyze_trajectory(self, member_id: UUID, family_id: UUID, days: int = 90) -> Dict[str, list]:
        """
        Analyzes the trajectory over the last N days.
        Returns structured observations.
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        res = await self._db.execute(
            select(HealthInsight)
            .where(HealthInsight.member_id == member_id, HealthInsight.created_at >= cutoff_date)
            .order_by(HealthInsight.created_at.asc())
        )
        insights = res.scalars().all()

        if not insights:
            return LongitudinalObservationSchema(
                trends=[],
                medication_effectiveness=[],
                disease_progression=[],
                new_risks=[],
                improvements=[],
                regressions=[],
            ).model_dump()

        # Build timeline context
        timeline_context = []
        for i in insights:
            timeline_context.append(f"[{i.created_at.date()}] {i.insight_type.upper()}: {i.description}")

        prompt = f"Time window: Last {days} days.\nTimeline:\n" + "\n".join(timeline_context)

        try:
            raw_dict = await self._llm.complete_structured(
                self.SYSTEM_PROMPT, prompt, response_schema=LongitudinalObservationSchema, max_tokens=1000
            )
            return raw_dict
        except Exception:
            return LongitudinalObservationSchema(
                trends=[],
                medication_effectiveness=[],
                disease_progression=[],
                new_risks=[],
                improvements=[],
                regressions=[],
            ).model_dump()
