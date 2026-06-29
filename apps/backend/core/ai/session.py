from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
import uuid

class AISession(BaseModel):
    """
    Context passed into every AI operation for tracking and observability.
    """
    request_id: UUID = Field(default_factory=uuid.uuid4)
    family_id: Optional[UUID] = None
    member_id: Optional[UUID] = None
    conversation_id: Optional[UUID] = None
    capability: str
    prompt_version: str
    model: str = "sarvam-default"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
