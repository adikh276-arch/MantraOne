from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models import KnowledgeGap
from core.domain.entities import FamilyDigitalTwin


class KnowledgeGapService:
    """
    Analyzes the FamilyDigitalTwin to detect contradictions, stale data, and missing evidence.
    Outputs structured KnowledgeGap objects.
    """

    def __init__(self, db: AsyncSession):
        self._db = db

    async def identify_gaps(self, twin: FamilyDigitalTwin, member_id: UUID) -> List[KnowledgeGap]:
        """
        Scans the twin for a specific member and returns a list of identified KnowledgeGaps.
        """
        member_id_str = str(member_id)
        gaps = []

        # 1. Missing Information from HealthState
        missing_info = twin.missing_information.get(member_id_str, [])
        for info in missing_info:
            gaps.append(
                KnowledgeGap(
                    family_id=twin.family_id,
                    member_id=member_id,
                    domain="general_health",
                    reason=info,
                    confidence=0.5,
                    clinical_priority="medium",
                    suggested_action="REQUEST_REPORT" if "lab" in info.lower() else "ASK_QUESTION",
                )
            )

        # 2. Preventive Needs
        preventive_needs = twin.preventive_needs.get(member_id_str, [])
        for p in preventive_needs:
            # We elevate missing monitoring to high clinical priority
            gaps.append(
                KnowledgeGap(
                    family_id=twin.family_id,
                    member_id=member_id,
                    domain=p.observation_type,  # e.g. missing_lab, medication_adherence
                    reason=p.description,
                    confidence=0.8,
                    clinical_priority="high",
                    suggested_action="ASK_QUESTION" if "adherence" in p.observation_type else "REQUEST_REPORT",
                )
            )

        # 3. Worsening trends with low evidence
        insights = twin.insights.get(member_id_str, [])
        for ins in insights:
            if ins.get("type") == "worsening":
                gaps.append(
                    KnowledgeGap(
                        family_id=twin.family_id,
                        member_id=member_id,
                        domain="symptom_progression",
                        reason=f"Worsening trend detected: {ins.get('desc')}. Need more context.",
                        confidence=0.9,
                        clinical_priority="high",
                        suggested_action="ASK_QUESTION",
                    )
                )

        # Persist gaps in DB (we might want to clear old active gaps first)
        # For simplicity in this implementation, we just return them and let the caller manage persistence if needed,
        # or we persist them here. We will persist them here so they can be scored later.

        if gaps:
            self._db.add_all(gaps)
            await self._db.commit()

        return gaps
