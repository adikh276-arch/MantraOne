from core.ai.registry import registry
from core.ai.session import AISession
from core.ai.prompt_manager import PromptManager


class ConversationAI:
    """
    Generates clinical replies bounded by the context builder.
    """

    def __init__(self):
        self._prompts = PromptManager()

    async def generate_reply(self, structured_context: dict, user_input: str, session: AISession) -> str:
        provider = registry.get("conversation")

        prompt = self._prompts.load_prompt(
            category="conversation",
            version_file="v1_clinical_reply.md",
            context={"clinical_context": str(structured_context), "user_input": user_input},
        )

        return await provider.generate_text(prompt_text=prompt, model=session.model)
