from datetime import datetime, timezone
from infrastructure.database.models import DomainConfidence

class ConfidenceCalculator:
    """
    Calculates dynamic confidence and freshness decay based on the type of health data.
    """
    
    # Define decay rates per week (as a percentage of freshness dropped per week)
    DECAY_RATES = {
        "lab_report": 0.02,        # Drops 2% per week
        "diagnosis": 0.00,         # Doesn't decay unless explicitly resolved
        "daily_checkin": 0.50,     # Drops 50% per week (very rapid)
        "medication": 0.05,        # Drops 5% per week (requires refills to prove active)
        "default": 0.10            # Drops 10% per week
    }

    def calculate_current_freshness(self, confidence_record: DomainConfidence, memory_type: str) -> float:
        """
        Calculates the current freshness of a domain based on time elapsed since last update
        and the specific decay profile of the memory type.
        """
        now = datetime.now(timezone.utc)
        
        # Ensure last_updated is timezone aware for math
        last_updated = confidence_record.last_updated
        if last_updated.tzinfo is None:
            last_updated = last_updated.replace(tzinfo=timezone.utc)
            
        weeks_elapsed = (now - last_updated).days / 7.0
        if weeks_elapsed < 0:
            weeks_elapsed = 0
            
        decay_rate = self.DECAY_RATES.get(memory_type, self.DECAY_RATES["default"])
        
        # Freshness is max(0, previous_freshness - (decay_rate * weeks_elapsed))
        new_freshness = max(0.0, confidence_record.freshness - (decay_rate * weeks_elapsed))
        return round(new_freshness, 3)
        
    def update_domain_confidence(self, confidence_record: DomainConfidence, new_evidence_confidence: float, memory_type: str) -> None:
        """
        Updates the domain confidence record with new incoming evidence.
        """
        # Recalculate current freshness before applying new data
        current_freshness = self.calculate_current_freshness(confidence_record, memory_type)
        
        # New evidence boosts freshness back up to 1.0 (or scales based on evidence confidence)
        # and adjusts overall confidence based on a weighted average of evidence.
        
        confidence_record.freshness = 1.0 # Fully fresh now
        confidence_record.evidence_count += 1
        
        # Simple moving average for confidence
        alpha = 0.3 # Weight of new evidence
        confidence_record.confidence = (confidence_record.confidence * (1 - alpha)) + (new_evidence_confidence * alpha)
        
        # Completeness roughly proxies by having sufficient evidence (e.g., 5 points = 1.0 completeness)
        confidence_record.completeness = min(1.0, confidence_record.evidence_count / 5.0)
        confidence_record.last_updated = datetime.now(timezone.utc)
