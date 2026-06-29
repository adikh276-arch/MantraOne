from core.ai.registry import registry
from core.ai.session import AISession


class SpeechAI:
    """
    Handles STT and TTS buffers, with streaming interfaces prepared.
    """

    async def transcribe(self, audio_data: bytes, session: AISession) -> str:
        provider = registry.get("speech_to_text")
        return await provider.speech_to_text(audio_data)

    async def synthesize(self, text: str, session: AISession) -> bytes:
        provider = registry.get("text_to_speech")
        return await provider.text_to_speech(text)

    async def detect_language(self, audio_data: bytes, session: AISession) -> str:
        # Mock detection
        return "hi-IN"
