from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import json

from infrastructure.database.models import ExplainabilityTrace

class ExplainabilityService:
    """
    Tracks and persists the reasoning chain for all generated knowledge
    (Insights, Preventive Observations, Chat Responses, Timeline Chapters).
    """

    def __init__(self, db: AsyncSession):
        self._db = db

    async def trace(
        self, 
        family_id: UUID, 
        member_id: UUID, 
        target_entity_type: str, 
        target_entity_id: UUID, 
        reasoning_source: str,
        confidence: float = 1.0,
        memories_used: Optional[List[str]] = None,
        timeline_events: Optional[List[str]] = None
    ) -> None:
        """
        Creates an ExplainabilityTrace record for a generated entity.
        """
        trace = ExplainabilityTrace(
            family_id=family_id,
            member_id=member_id,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            reasoning_source=reasoning_source,
            confidence=confidence,
            memories_used=memories_used or [],
            timeline_events_referenced=timeline_events or []
        )
        self._db.add(trace)
        await self._db.commit()
