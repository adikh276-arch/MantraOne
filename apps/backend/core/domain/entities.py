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
    source_entity_id: UUID
    watcher_domains: list[str] = Field(default_factory=list)
    confidence: float = Field(1.0, description="Confidence in this memory")
    freshness: float = Field(1.0, description="Freshness of the memory")
    source_reliability: float = Field(1.0, description="Reliability of the source")
    verification_status: str = Field("unverified", description="verified, unverified, disputed")
    corroboration_count: int = Field(0, description="Number of times corroborated")
    last_verified_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PreventiveObservationContext(BaseModel):
    id: UUID
    observation_type: str
    description: str
    status: str
    created_at: datetime

class TimelineChapter(BaseModel):
    title: str
    description: str
    start_date: datetime
    end_date: datetime | None = None
    events: list[dict] = Field(default_factory=list)

class FamilyDigitalTwin(BaseModel):
    family_id: UUID
    members: list[dict] = Field(default_factory=list) # Basic demographics
    health_states: dict[str, dict] = Field(default_factory=dict) # member_id -> state summary
    active_conditions: dict[str, list[str]] = Field(default_factory=dict)
    risks: dict[str, list[str]] = Field(default_factory=dict)
    medications: dict[str, list[str]] = Field(default_factory=dict)
    confidence_scores: dict[str, dict] = Field(default_factory=dict) # domain -> scores
    preventive_needs: dict[str, list[PreventiveObservationContext]] = Field(default_factory=dict)
    missing_information: dict[str, list[str]] = Field(default_factory=dict)
    timeline_chapters: dict[str, list[TimelineChapter]] = Field(default_factory=dict)
    follow_ups: dict[str, list[dict]] = Field(default_factory=dict)
    insights: dict[str, list[dict]] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClinicalContext(BaseModel):
    patient_summary: dict = Field(default_factory=dict)
    active_conditions: list[str] = Field(default_factory=list)
    current_medications: list[str] = Field(default_factory=list)
    recent_changes: list[str] = Field(default_factory=list)
    timeline_summary: list[dict] = Field(default_factory=list)
    confidence: dict = Field(default_factory=dict)
    missing_information: list[str] = Field(default_factory=list)
    pending_followups: list[dict] = Field(default_factory=list)
    family_context: dict = Field(default_factory=dict)
    retrieved_memories: list[MemoryFragment] = Field(default_factory=list)

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
    freshness: float = 1.0
    source_reliability: float = 1.0
    verification_status: str = "unverified"
    corroboration_count: int = 0
    last_verified_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ForgetResult(BaseModel):
    family_id: UUID
    member_id: UUID | None
    records_deleted: int
    memory_cleared: bool

class TimelineEvent(BaseModel):
    date: datetime
    title: str
    description: str
    domains: list[str] = Field(default_factory=list)

class Timeline(BaseModel):
    member_id: UUID
    events: list[TimelineEvent]

class MedicationHistory(BaseModel):
    member_id: UUID
    active_medications: list[str]
    stopped_medications: list[str]
    interactions_flagged: bool

class RiskSummary(BaseModel):
    member_id: UUID
    high_risk_domains: list[str]
    clinical_summary: str
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
