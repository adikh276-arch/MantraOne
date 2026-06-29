from typing import Any, Dict, Optional, Type
from pydantic import BaseModel
import asyncio
import os
import json

from core.providers.ai_provider import AIProvider
from core.ai.validation import generate_with_retry
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


class SarvamProvider(AIProvider):
    """
    Default AI Provider implementing the Sarvam MCP server integration.
    Communicates dynamically with the pre-configured MCP server.
    """

    def __init__(self):
        # We assume the MCP endpoint parameters are configured by the environment
        # e.g., executing `uvx sarvam-mcp` locally via stdio.
        # In a real deployed environment, it might connect via SSE.
        self._server_params = StdioServerParameters(
            command="uvx", args=["sarvam-mcp"], env={"SARVAM_API_KEY": os.getenv("SARVAM_API_KEY", "")}
        )
        # We establish the connection dynamically when needed, or manage a pool.
        # For this prototype, we'll open the session inline.

    async def initialize(self) -> None:
        pass

    async def generate_structured(
        self, prompt_text: str, response_model: Type[BaseModel], model: Optional[str] = None
    ) -> BaseModel:
        """
        Input -> Prompt -> Sarvam -> JSON -> Validate -> Domain Object
        """

        async def call_sarvam():
            async with stdio_client(self._server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    # We assume Sarvam exposes a generic generation tool or we use its translation/ocr tools directly.
                    # For generic reasoning/extraction, we mock the tool call logic.
                    # result = await session.call_tool("sarvam_generate", {"prompt": prompt_text, "format": "json"})
                    # return result.content[0].text

                    # Mock response for testing extraction logic
                    return '{"diagnoses": [], "medications": []}'

        return await generate_with_retry(call_sarvam, response_model)

    async def generate_text(self, prompt_text: str, model: Optional[str] = None) -> str:
        async with stdio_client(self._server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # Mock result
                return "Generated plain text from Sarvam."

    async def ocr(self, file_path: str) -> str:
        async with stdio_client(self._server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # In real scenario: result = await session.call_tool("sarvam_ocr", {"file_path": file_path})
                return "Extracted OCR text."

    async def translate(self, text: str, target_language: str) -> str:
        async with stdio_client(self._server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # result = await session.call_tool("sarvam_translate", {"text": text, "target_language": target_language})
                return "Translated text."

    async def speech_to_text(self, audio_data: bytes) -> str:
        async with stdio_client(self._server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # result = await session.call_tool("sarvam_speech_to_text", {"audio_base64": ...})
                return "Transcribed text."

    async def text_to_speech(self, text: str) -> bytes:
        async with stdio_client(self._server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # result = await session.call_tool("sarvam_text_to_speech", {"text": text})
                return b"audio_bytes"
