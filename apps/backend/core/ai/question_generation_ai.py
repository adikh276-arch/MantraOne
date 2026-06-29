from core.ai.registry import registry
from core.ai.session import AISession
from core.ai.prompt_manager import PromptManager


class QuestionGenerationAI:
    """
    Optional LLM refinement for parameterized adaptive question templates.
    """

    def __init__(self):
        self._prompts = PromptManager()

    async def refine_question(self, draft_question: str, context: dict, session: AISession) -> str:
        provider = registry.get("question_generation")

        prompt = self._prompts.load_prompt(
            category="adaptive_question",
            version_file="v1_refinement.md",
            context={"draft_question": draft_question, "context": str(context)},
        )

        return await provider.generate_text(prompt_text=prompt, model=session.model)
