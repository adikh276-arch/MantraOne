from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from infrastructure.database.models import Conversation, Message
from core.providers.llm_provider import LLMProvider
from core.providers.memory_provider import MemoryProvider
import structlog
from typing import AsyncGenerator

logger = structlog.get_logger()

class ConversationService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._llm = LLMProvider()
        self._memory = MemoryProvider()

    async def create_conversation(self, family_id: UUID, member_id: UUID, title: str | None = None) -> Conversation:
        conversation = Conversation(
            family_id=family_id,
            member_id=member_id,
            title=title or "New Conversation"
        )
        self._db.add(conversation)
        await self._db.commit()
        await self._db.refresh(conversation)
        return conversation

    async def get_conversation(self, conversation_id: UUID) -> Conversation | None:
        result = await self._db.execute(select(Conversation).filter_by(id=conversation_id))
        return result.scalars().first()

    async def list_messages(self, conversation_id: UUID) -> list[Message]:
        result = await self._db.execute(
            select(Message)
            .filter_by(conversation_id=conversation_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())

    async def send_message_stream(self, conversation_id: UUID, member_id: UUID, family_id: UUID, text: str) -> AsyncGenerator[str, None]:
        # Save user message
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=text
        )
        self._db.add(user_msg)
        await self._db.commit()
        
        # Retrieve context from MemoryProvider
        fragments = await self._memory.recall(text, family_id=family_id, member_id=member_id)
        context = "\n".join([f"- {f.content}" for f in fragments]) if fragments else "No specific past context found."
        
        # Prepare system prompt
        system_prompt = (
            "You are MantraOne, a compassionate health companion.\n"
            f"Context from memory:\n{context}\n\n"
            "Provide a helpful, empathetic response."
        )
        
        # In a real streaming implementation with AsyncOpenAI, we would stream chunks
        # Since we use LLMProvider which currently returns a full string, we will mock streaming for now
        # OR we can add streaming to LLMProvider! For now, we simulate stream.
        full_response = await self._llm.complete(system_prompt=system_prompt, user_prompt=text, max_tokens=1000)
        
        # Stream chunks (mocked streaming simulation for the frontend contract)
        # To truly stream, LLMProvider needs an async generator.
        chunk_size = 20
        for i in range(0, len(full_response), chunk_size):
            yield full_response[i:i+chunk_size]
            
        # Save assistant message
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=full_response
        )
        self._db.add(assistant_msg)
        await self._db.commit()
