from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from infrastructure.database.models import UserFatigueMetrics

class UserFatigueService:
    """
    Tracks and computes a fatigue multiplier (0.0 to 1.0) based on interaction history.
    1.0 means fully receptive, 0.0 means completely fatigued (do not disturb).
    """
    
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_fatigue_multiplier(self, member_id: UUID) -> float:
        """
        Calculates the fatigue multiplier.
        """
        res = await self._db.execute(select(UserFatigueMetrics).where(UserFatigueMetrics.member_id == member_id))
        metrics = res.scalar_one_or_none()
        
        if not metrics:
            return 1.0 # Brand new, fully receptive
            
        # Example logic:
        # If user ignored the last 3 questions, heavily penalize.
        ignore_ratio = metrics.questions_ignored / (metrics.questions_asked or 1)
        
        multiplier = 1.0
        
        if ignore_ratio > 0.5:
            multiplier *= 0.5
            
        if metrics.questions_asked > 5:
            # High volume penalty
            multiplier *= 0.8
            
        if metrics.last_interaction_at:
            # If we asked a question less than 4 hours ago, penalize
            hours_since = (datetime.now(timezone.utc) - metrics.last_interaction_at).total_seconds() / 3600
            if hours_since < 4:
                multiplier *= 0.2
            elif hours_since > 48:
                # Recovered
                multiplier = min(1.0, multiplier * 1.5)
                
        return max(0.01, min(1.0, multiplier)) # Clamp between 0.01 and 1.0

    async def record_interaction(self, member_id: UUID, interaction_type: str) -> None:
        """
        Records an interaction (asked, answered, ignored).
        """
        res = await self._db.execute(select(UserFatigueMetrics).where(UserFatigueMetrics.member_id == member_id))
        metrics = res.scalar_one_or_none()
        
        if not metrics:
            metrics = UserFatigueMetrics(member_id=member_id)
            self._db.add(metrics)
            
        metrics.last_interaction_at = datetime.now(timezone.utc)
        
        if interaction_type == "asked":
            metrics.questions_asked += 1
        elif interaction_type == "answered":
            metrics.questions_answered += 1
        elif interaction_type == "ignored":
            metrics.questions_ignored += 1
            
        await self._db.commit()
