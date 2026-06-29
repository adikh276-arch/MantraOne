from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.providers.llm_provider import LLMProvider
from infrastructure.database.models import HealthInsight
import structlog

logger = structlog.get_logger()

class InsightGenerationSchema(BaseModel):
    detected_changes: List[str] = Field(default_factory=list, description="New diagnoses, new medications, abnormal lab results.")
    improving_conditions: List[str] = Field(default_factory=list, description="Conditions that show improvement.")
    worsening_conditions: List[str] = Field(default_factory=list, description="Conditions that show decline.")
    missing_information: List[str] = Field(default_factory=list, description="Gaps in the clinical context.")
    clinical_observations: List[str] = Field(default_factory=list, description="General observations.")
    confidence: float = Field(..., description="Overall confidence in these insights (0.0 to 1.0).")

class HealthInsightService:
    """
    Generates structured health insights from newly ingested data using LLM extraction,
    and manages the lifecycle of these insights in the database.
    """
    
    SYSTEM_PROMPT = """You are a highly precise clinical intelligence engine.
    Analyze the provided new health data and the existing patient context.
    Identify detected changes, improving/worsening conditions, and missing information.
    Return ONLY a valid JSON object matching the exact requested schema. Do not include markdown formatting.
    """

    def __init__(self, db: AsyncSession):
        self._db = db
        self._llm = LLMProvider()

    async def generate_insights(self, member_id: UUID, family_id: UUID, new_data: str, current_context_summary: str) -> None:
        """
        Analyzes new data against current context to generate structured insights.
        """
        prompt = f"Current Context:\n{current_context_summary}\n\nNew Ingested Data:\n{new_data}\n\nGenerate structured insights."
        
        try:
            raw_dict = await self._llm.complete_structured(
                self.SYSTEM_PROMPT,
                prompt,
                response_schema=InsightGenerationSchema,
                max_tokens=1500
            )
            parsed_insights = InsightGenerationSchema(**raw_dict)
            await self._store_insights(member_id, family_id, parsed_insights)
        except Exception as e:
            logger.error("insight_generation_failed", error=str(e), member_id=member_id)

    async def _store_insights(self, member_id: UUID, family_id: UUID, parsed: InsightGenerationSchema) -> None:
        """
        Translates the Pydantic schema into HealthInsight DB records.
        Handles the lifecycle (e.g., if a change was already detected, maybe update it instead of duplicate).
        """
        # For simplicity in this implementation, we will archive older generated insights 
        # and create new ones, keeping the state fresh. A more robust implementation would diff them.
        
        # Archive old active insights for this member
        res = await self._db.execute(
            select(HealthInsight).where(
                HealthInsight.member_id == member_id,
                HealthInsight.status.in_(["active", "updated", "generated"])
            )
        )
        old_insights = res.scalars().all()
        for old in old_insights:
            old.status = "archived"
            self._db.add(old)

        # Store new insights
        new_records = []
        
        for change in parsed.detected_changes:
            new_records.append(HealthInsight(
                family_id=family_id, member_id=member_id,
                insight_type="alert", description=change,
                structured_data={"confidence": parsed.confidence},
                status="active"
            ))
            
        for obs in parsed.clinical_observations:
            new_records.append(HealthInsight(
                family_id=family_id, member_id=member_id,
                insight_type="summary", description=obs,
                structured_data={"confidence": parsed.confidence},
                status="active"
            ))
            
        for gap in parsed.missing_information:
            new_records.append(HealthInsight(
                family_id=family_id, member_id=member_id,
                insight_type="gap", description=gap,
                structured_data={"confidence": parsed.confidence},
                status="active"
            ))
            
        if parsed.improving_conditions or parsed.worsening_conditions:
            new_records.append(HealthInsight(
                family_id=family_id, member_id=member_id,
                insight_type="trend", 
                description="Recent trajectory analysis reveals changing condition statuses.",
                structured_data={
                    "improving_conditions": parsed.improving_conditions,
                    "worsening_conditions": parsed.worsening_conditions,
                    "confidence": parsed.confidence
                },
                status="active"
            ))

        self._db.add_all(new_records)
        await self._db.commit()
