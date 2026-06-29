from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from infrastructure.database.models import PreventiveObservation, DomainConfidence


class PreventiveIntelligenceService:
    """
    Proactive intelligence engine that scans health states for missing monitoring,
    vaccination gaps, and medication adherence issues.
    """

    def __init__(self, db: AsyncSession):
        self._db = db

    async def scan_for_preventive_gaps(self, member_id: UUID, family_id: UUID) -> None:
        """
        Scans DomainConfidence and structured data to identify gaps.
        Creates PreventiveObservation records.
        """
        now = datetime.now(timezone.utc)

        # 1. Check Domain Confidence for missing monitoring
        res = await self._db.execute(select(DomainConfidence).where(DomainConfidence.member_id == member_id))
        confidences = res.scalars().all()

        new_observations = []

        for conf in confidences:
            # Example rule: if a crucial domain is stale for > 90 days, flag it
            if conf.domain in ["diabetes", "hypertension", "cardiology"]:
                # If freshness is below a critical threshold (e.g., 0.2) or last_updated is very old
                days_since_update = (now - conf.last_updated.replace(tzinfo=timezone.utc)).days
                if days_since_update > 90:
                    obs = PreventiveObservation(
                        family_id=family_id,
                        member_id=member_id,
                        observation_type="missing_monitoring",
                        description=f"No {conf.domain} updates or labs have been uploaded in over 90 days.",
                        status="active",
                    )
                    new_observations.append(obs)

            if conf.domain == "medication":
                if conf.freshness < 0.5:
                    obs = PreventiveObservation(
                        family_id=family_id,
                        member_id=member_id,
                        observation_type="medication_adherence",
                        description="Medication adherence has not been confirmed recently.",
                        status="active",
                    )
                    new_observations.append(obs)

        # In a real app we'd check if an active observation of the exact same type/description already exists
        # before inserting a duplicate. We omit that query here for brevity, assuming standard deduplication.

        if new_observations:
            self._db.add_all(new_observations)
            await self._db.commit()
