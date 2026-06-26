from __future__ import annotations
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, date, timezone
from core.domain.enums import HealthEventType, WatcherDomain, SignalSeverity

class BaseHealthEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: HealthEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    idempotency_key: str = Field(default="")
    
    def model_post_init(self, __context) -> None:
        if not self.idempotency_key:
            self.idempotency_key = str(self.event_id)

class CheckinSubmittedEvent(BaseHealthEvent):
    event_type: HealthEventType = HealthEventType.CHECKIN_SUBMITTED
    checkin_id: UUID
    member_id: UUID
    family_id: UUID
    domain: str
    checkin_date: date

class HealthMetricRecordedEvent(BaseHealthEvent):
    event_type: HealthEventType = HealthEventType.HEALTH_METRIC_RECORDED
    metric_id: UUID
    member_id: UUID
    family_id: UUID
    metric_type: str
    recorded_at: datetime

class MedicationLoggedEvent(BaseHealthEvent):
    event_type: HealthEventType = HealthEventType.MEDICATION_LOGGED
    log_id: UUID
    medication_id: UUID
    member_id: UUID
    family_id: UUID
    status: str

class DocumentProcessedEvent(BaseHealthEvent):
    event_type: HealthEventType = HealthEventType.DOCUMENT_PROCESSED
    document_id: UUID
    member_id: UUID
    family_id: UUID
    document_type: str
    extracted_entities: list[str] = Field(default_factory=list)

class WatcherSignalEmittedEvent(BaseHealthEvent):
    event_type: HealthEventType = HealthEventType.WATCHER_SIGNAL_EMITTED
    signal_id: UUID
    member_id: UUID
    family_id: UUID
    watcher_domain: WatcherDomain
    severity: SignalSeverity
    signal_type: str

class CoordinatorDecidedEvent(BaseHealthEvent):
    event_type: HealthEventType = HealthEventType.COORDINATOR_DECIDED
    decision_id: UUID
    member_id: UUID
    family_id: UUID
    selected_domain: WatcherDomain
    checkin_question: str | None = None

class EscalationTriggeredEvent(BaseHealthEvent):
    event_type: HealthEventType = HealthEventType.ESCALATION_TRIGGERED
    escalation_id: UUID
    member_id: UUID
    family_id: UUID
    urgency_level: str
    recommended_specialty: str

class MemoryIngestedEvent(BaseHealthEvent):
    event_type: HealthEventType = HealthEventType.MEMORY_INGESTED
    source_entity_type: str
    source_entity_id: UUID
    member_id: UUID
    family_id: UUID
    cognee_memory_id: str

class DocumentUploadedEvent(BaseHealthEvent):
    event_type: HealthEventType = HealthEventType.DOCUMENT_UPLOADED
    document_id: UUID
    member_id: UUID
    family_id: UUID
    document_type: str
    gcs_path: str

class DocumentExtractedEvent(BaseHealthEvent):
    event_type: HealthEventType = HealthEventType.DOCUMENT_EXTRACTED
    document_id: UUID
    member_id: UUID
    family_id: UUID
    extracted_text_length: int
    mime_type: str

EVENT_TYPE_MAP: dict[HealthEventType, type[BaseHealthEvent]] = {
    HealthEventType.CHECKIN_SUBMITTED: CheckinSubmittedEvent,
    HealthEventType.HEALTH_METRIC_RECORDED: HealthMetricRecordedEvent,
    HealthEventType.MEDICATION_LOGGED: MedicationLoggedEvent,
    HealthEventType.DOCUMENT_PROCESSED: DocumentProcessedEvent,
    HealthEventType.WATCHER_SIGNAL_EMITTED: WatcherSignalEmittedEvent,
    HealthEventType.COORDINATOR_DECIDED: CoordinatorDecidedEvent,
    HealthEventType.ESCALATION_TRIGGERED: EscalationTriggeredEvent,
    HealthEventType.MEMORY_INGESTED: MemoryIngestedEvent,
    HealthEventType.DOCUMENT_UPLOADED: DocumentUploadedEvent,
    HealthEventType.DOCUMENT_EXTRACTED: DocumentExtractedEvent,
}
