from core.ai.registry import registry
from core.ai.session import AISession
from core.ai.prompt_manager import PromptManager


class TimelineAI:
    """
    Generates human-readable chronological narratives from structured timeline objects.
    """

    def __init__(self):
        self._prompts = PromptManager()

    async def narrate_timeline(self, structured_timeline: dict, session: AISession) -> str:
        provider = registry.get("timeline")

        prompt = self._prompts.load_prompt(
            category="timeline", version_file="v1_chronology.md", context={"timeline_events": str(structured_timeline)}
        )

        return await provider.generate_text(prompt_text=prompt, model=session.model)
