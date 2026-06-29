from pydantic import BaseModel
from typing import Optional
from core.ai.registry import registry
from core.ai.session import AISession
from core.ai.prompt_manager import PromptManager


class GenericSummaryResult(BaseModel):
    summary: str
    key_points: list[str] = []


class SummarizationAI:
    """
    Generates domain-specific summaries from structured data.
    """

    def __init__(self):
        self._prompts = PromptManager()

    async def summarize(self, instructions: str, data: dict, session: AISession) -> GenericSummaryResult:
        provider = registry.get("summarization")

        prompt = self._prompts.load_prompt(
            category="summarization",
            version_file="v1_summarize.md",
            context={"instructions": instructions, "data": str(data)},
        )

        return await provider.generate_structured(
            prompt_text=prompt, response_model=GenericSummaryResult, model=session.model
        )
