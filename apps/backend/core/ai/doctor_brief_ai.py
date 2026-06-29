from pydantic import BaseModel
from typing import List, Optional
from core.ai.registry import registry
from core.ai.session import AISession
from core.ai.prompt_manager import PromptManager

class DoctorBriefResult(BaseModel):
    chief_concern: str
    timeline_14_days: List[str] = []
    recent_changes: List[str] = []
    active_medications: List[str] = []
    supporting_evidence: List[str] = []
    missing_information: List[str] = []
    outstanding_questions: List[str] = []
    confidence_bounds: dict = {}
    suggested_discussion_topics: List[str] = []

class DoctorBriefAI:
    """
    Synthesizes clinical handoff summaries.
    """
    def __init__(self):
        self._prompts = PromptManager()
        
    async def generate_brief(self, digital_twin: dict, session: AISession) -> DoctorBriefResult:
        provider = registry.get("doctor_brief")
        
        prompt = self._prompts.load_prompt(
            category="doctor_brief", 
            version_file="v1_handoff.md",
            context={
                "digital_twin": str(digital_twin)
            }
        )
        
        return await provider.generate_structured(
            prompt_text=prompt,
            response_model=DoctorBriefResult,
            model=session.model
        )
