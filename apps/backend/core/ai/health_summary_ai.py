from pydantic import BaseModel
from core.ai.registry import registry
from core.ai.session import AISession
from core.ai.prompt_manager import PromptManager

class HealthSummaryResult(BaseModel):
    timeframe: str
    executive_summary: str
    notable_changes: list[str] = []
    action_items: list[str] = []

class HealthSummaryAI:
    """
    Generates top-level member and family structured summaries.
    """
    def __init__(self):
        self._prompts = PromptManager()
        
    async def generate_summary(self, timeframe: str, health_context: dict, session: AISession) -> HealthSummaryResult:
        provider = registry.get("health_summary")
        
        prompt = self._prompts.load_prompt(
            category="health_summary", 
            version_file="v1_family_rollup.md",
            context={
                "summary_timeframe": timeframe,
                "health_context": str(health_context)
            }
        )
        
        return await provider.generate_structured(
            prompt_text=prompt,
            response_model=HealthSummaryResult,
            model=session.model
        )
