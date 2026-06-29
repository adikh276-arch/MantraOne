from uuid import UUID
from typing import Dict, Any

from infrastructure.database.models import EscalationEvent
from core.domain.entities import FamilyDigitalTwin

class ClinicalHandoffService:
    """
    Consumes an EscalationEvent and the FamilyDigitalTwin to generate a structured 
    Doctor Brief artifact to reduce repeated questioning during a consultation.
    """
    
    async def generate_doctor_brief(self, event: EscalationEvent, twin: FamilyDigitalTwin) -> Dict[str, Any]:
        """
        Creates the structured payload for a clinician.
        """
        member_id_str = str(event.member_id)
        
        # 1. Gather Active Medications
        medications = [
            m.get("description") for m in twin.preventive_needs.get(member_id_str, []) 
            if "adherence" in m.get("observation_type", "")
        ]
        
        # 2. Extract specific timelines from insights
        recent_changes = twin.insights.get(member_id_str, [])
        
        # 3. Pull confidence and missing information bounds
        missing_info = twin.missing_information.get(member_id_str, [])
        confidence = twin.confidence_scores.get(member_id_str, {})
        
        brief = {
            "patient_summary": f"Patient {member_id_str}",
            "current_concern": event.escalation_reason,
            "escalation_urgency": event.urgency_level,
            "recent_changes": recent_changes,
            "active_medications": medications,
            "missing_information": missing_info,
            "ai_confidence_bounds": confidence,
            "reason_for_escalation": "Automated deterministic threshold triggered by persistent deterioration."
        }
        
        return brief
