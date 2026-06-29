from typing import Optional
from datetime import datetime, timedelta, timezone


class ClinicalRulesEngine:
    """
    Deterministic rules engine for determining clinical follow-up intervals based on diagnoses,
    medications, or other clinical events.
    """

    # Simple rule map: Condition/Entity -> Follow-up Interval in Days
    FOLLOW_UP_INTERVALS = {
        # Diagnoses
        "diabetes": 90,
        "type 2 diabetes": 90,
        "hypertension": 30,
        "high blood pressure": 30,
        "asthma": 180,
        "hypothyroidism": 180,
        # Acute conditions
        "fever": 3,
        "urinary tract infection": 7,
        "uti": 7,
        "strep throat": 7,
        "bronchitis": 14,
        # Default fallback for new medications
        "new_medication": 14,
    }

    def determine_follow_up(self, entity_name: str, entity_type: str = "diagnosis") -> Optional[timedelta]:
        """
        Determines the deterministic follow-up interval for a given entity.
        Returns a timedelta if a rule matches, else None.
        """
        normalized_name = entity_name.lower().strip()

        if normalized_name in self.FOLLOW_UP_INTERVALS:
            return timedelta(days=self.FOLLOW_UP_INTERVALS[normalized_name])

        if entity_type == "medication":
            return timedelta(days=self.FOLLOW_UP_INTERVALS["new_medication"])

        return None

    def calculate_due_date(
        self, entity_name: str, entity_type: str, base_date: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        Calculates the exact due date for a follow up.
        """
        interval = self.determine_follow_up(entity_name, entity_type)
        if not interval:
            return None

        if not base_date:
            base_date = datetime.now(timezone.utc)

        return base_date + interval
