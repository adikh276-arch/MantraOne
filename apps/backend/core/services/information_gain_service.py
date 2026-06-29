from infrastructure.database.models import KnowledgeGap

class InformationGainService:
    """
    Scores candidate actions (like Ask, Wait, Remind) by maximizing:
    InfoGain * Importance * ConfidenceImprovement / (Effort * Fatigue).
    """

    def score_gap(self, gap: KnowledgeGap, fatigue_multiplier: float) -> float:
        """
        Calculates the priority score for attempting to resolve a KnowledgeGap.
        """
        # Baseline multipliers based on priority
        priority_map = {
            "high": 1.0,
            "medium": 0.5,
            "low": 0.2
        }
        importance = priority_map.get(gap.clinical_priority.lower(), 0.1)
        
        # InfoGain is higher if confidence is currently very low
        info_gain = 1.0 - gap.confidence
        
        # Assume standard effort for a multiple choice question
        effort = 0.2
        
        # Priority Score Formula
        # If fatigue is high (multiplier is close to 0), score tanks.
        score = (info_gain * importance * fatigue_multiplier) / effort
        
        return score
