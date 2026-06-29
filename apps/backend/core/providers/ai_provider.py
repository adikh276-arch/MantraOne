from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel

class AIProvider(ABC):
    """
    Abstract interface for all AI capabilities in MantraOne.
    Implementations (like SarvamProvider) handle the transport and specific integrations.
    """
    
    @abstractmethod
    async def initialize(self) -> None:
        pass

    @abstractmethod
    async def generate_structured(
        self, 
        prompt_text: str, 
        response_model: Type[BaseModel],
        model: Optional[str] = None
    ) -> BaseModel:
        """
        Generates a structured Pydantic model from a prompt.
        """
        pass
        
    @abstractmethod
    async def generate_text(self, prompt_text: str, model: Optional[str] = None) -> str:
        """
        Generates plain text (e.g. for translation, narrative).
        """
        pass
        
    @abstractmethod
    async def ocr(self, file_path: str) -> str:
        """
        Extracts raw text from a document/image.
        """
        pass
        
    @abstractmethod
    async def translate(self, text: str, target_language: str) -> str:
        """
        Translates medical text.
        """
        pass
        
    @abstractmethod
    async def speech_to_text(self, audio_data: bytes) -> str:
        """
        Transcribes audio.
        """
        pass
        
    @abstractmethod
    async def text_to_speech(self, text: str) -> bytes:
        """
        Synthesizes audio.
        """
        pass
