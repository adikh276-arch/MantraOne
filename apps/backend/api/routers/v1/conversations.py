from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from uuid import UUID
from pydantic import BaseModel
from api.dependencies import get_db, get_current_user
from core.services.conversation_service import ConversationService

router = APIRouter()


class CreateConversationRequest(BaseModel):
    family_id: UUID
    member_id: UUID
    title: str | None = None


class SendMessageRequest(BaseModel):
    family_id: UUID
    member_id: UUID
    text: str


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: str


@router.post("/")
async def create_conversation(
    req: CreateConversationRequest, db: AsyncSession = Depends(get_db), user: dict[str, Any] = Depends(get_current_user)
):
    service = ConversationService(db)
    conv = await service.create_conversation(req.family_id, req.member_id, req.title)
    return {"id": conv.id, "title": conv.title}


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: UUID, db: AsyncSession = Depends(get_db), user: dict[str, Any] = Depends(get_current_user)
):
    service = ConversationService(db)
    messages = await service.list_messages(conversation_id)
    return {
        "messages": [
            {"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at.isoformat()} for m in messages
        ]
    }


@router.post("/{conversation_id}/messages")
async def send_message(
    conversation_id: UUID,
    req: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
):
    service = ConversationService(db)
    # Return a streaming response
    return StreamingResponse(
        service.send_message_stream(conversation_id, req.member_id, req.family_id, req.text),
        media_type="text/event-stream",
    )
