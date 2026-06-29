from core.ai.registry import registry
from core.ai.session import AISession

class OCRAI:
    """
    Handles OCR capability using the configured AI Provider.
    """
    async def extract_text(self, file_path: str, session: AISession) -> str:
        provider = registry.get("ocr")
        
        # In a real app we'd log the session tracking here before/after the call
        return await provider.ocr(file_path)
