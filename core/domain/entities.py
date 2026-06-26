from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import timezone
from core.domain.enums import (
    WatcherDomain, SignalSeverity, SignalType, TrendDirection,
    MemoryType, UrgencyLevel, EscalationStatus, MemberRelationship,
    SelectionReason,
)

@dataclass
class FamilyMemberEntity:
    id: UUID
    family_id: UUID
    firebase_uid: str | None
    name: str
    relationship: MemberRelationship
    is_primary: bool
    timezone: str
    health_profile_complete: bool
    gender: str | None = None
    preferred_language: str = "en"
    avatar_url: str | None = None

@dataclass
class WatcherSignalEntity:
    id: UUID
    family_id: UUID
    member_id: UUID
    watcher_domain: WatcherDomain
    signal_date: date
    signal_type: SignalType
    severity: SignalSeverity
    signal_payload: dict
    deviation_from_baseline: float | None
    trend_direction: TrendDirection | None
    supporting_data: dict | None
    surfaced: bool
    expires_at: datetime | None
    created_at: datetime

@dataclass
class CoordinatorDecisionEntity:
    id: UUID
    family_id: UUID
    member_id: UUID
    decision_date: date
    selected_domain: WatcherDomain
    selection_reason: SelectionReason
    selected_signal_ids: list[UUID]
    suppressed_domains: list[str]
    checkin_count_today: int
    user_busy_signal: bool
    checkin_generated: str | None
    delivered_at: datetime | None
    responded_at: datetime | None

@dataclass
class EscalationEventEntity:
    id: UUID
    family_id: UUID
    member_id: UUID
    triggered_at: datetime
    triggering_signals: list[dict]
    convergence_score: float
    recommended_specialty: str
    escalation_reason: str
    urgency_level: UrgencyLevel
    status: EscalationStatus
    consultation_id: UUID | None = None

class MemoryFragment(BaseModel):
    content: str
    score: float
    member_id: UUID
    family_id: UUID
    memory_type: MemoryType
    timestamp: datetime
    source_entity_type: str
    source_entity_id: UUID
    watcher_domains: list[str] = Field(default_factory=list)

class HealthContext(BaseModel):
    member_id: UUID
    family_id: UUID
    domains: list[str]
    lookback_days: int
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    recent_signals: list[dict] = Field(default_factory=list)
    memory_fragments: list[MemoryFragment] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class HealthMemoryMetadata(BaseModel):
    family_id: UUID
    member_id: UUID
    memory_type: MemoryType
    watcher_domains: list[str] = Field(default_factory=list)
    timestamp: datetime
    source_entity_type: str
    source_entity_id: UUID
    confidence: float = 1.0

class ForgetResult(BaseModel):
    family_id: UUID
    member_id: UUID | None
    records_deleted: int
    memory_cleared: bool
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
