from __future__ import annotations
import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    String, Boolean, Integer, Float, Text, Date,
    ForeignKey, UniqueConstraint, Index, BigInteger, func, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import mapped_column, Mapped, relationship as orm_relationship
from infrastructure.database.session import Base
from sqlalchemy import DateTime

TIMESTAMPTZ = DateTime(timezone=True)

class Family(Base):
    __tablename__ = "families"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    primary_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    subscription_tier: Mapped[str] = mapped_column(String(50), default="basic", nullable=False)
    subscription_valid_until: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    onboarding_completed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    health_baseline_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    members: Mapped[list[FamilyMember]] = orm_relationship(back_populates="family", lazy="noload")
    __table_args__ = (Index("idx_families_primary_user", "primary_user_id"),)

class FamilyMember(Base):
    __tablename__ = "family_members"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    firebase_uid: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    date_of_birth: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    relationship: Mapped[str] = mapped_column(String(100), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(100), default="Asia/Kolkata", nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="standard", nullable=False)
    health_profile_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    family: Mapped[Family] = orm_relationship(back_populates="members", lazy="noload")  # type: ignore
    __table_args__ = (Index("idx_members_family", "family_id"), Index("idx_members_firebase_uid", "firebase_uid"),)

class HealthBaseline(Base):
    __tablename__ = "health_baselines"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    baseline_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    calculated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    data_points_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    __table_args__ = (UniqueConstraint("member_id", "domain", name="uq_baseline_member_domain"), Index("idx_baselines_member_domain", "member_id", "domain"),)

class DailyCheckin(Base):
    __tablename__ = "daily_checkins"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    checkin_date: Mapped[date] = mapped_column(Date, nullable=False)
    checkin_time: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    structured_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_initiated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    coordinator_decision_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    memory_ingested: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    memory_ingested_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    __table_args__ = (UniqueConstraint("member_id", "checkin_date", "domain", name="uq_checkin_member_date_domain"), Index("idx_checkins_member_date", "member_id", "checkin_date"), Index("idx_checkins_family_date", "family_id", "checkin_date"),)

class WatcherSignal(Base):
    __tablename__ = "watcher_signals"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    watcher_domain: Mapped[str] = mapped_column(String(100), nullable=False)
    signal_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    signal_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    signal_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    deviation_from_baseline: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    trend_direction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    supporting_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    surfaced: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    surfaced_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    __table_args__ = (Index("idx_signals_member_domain", "member_id", "watcher_domain", "signal_date"), Index("idx_signals_unsurfaced", "family_id", "surfaced", "severity", "created_at"),)

class DomainConfidence(Base):
    __tablename__ = "domain_confidences"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    completeness: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    freshness: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("member_id", "domain", name="uq_domain_confidence_member_domain"),
        Index("idx_domain_confidences_member", "member_id"),
    )

class HealthInsight(Base):
    __tablename__ = "health_insights"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    insight_type: Mapped[str] = mapped_column(String(50), nullable=False) # trend, alert, gap, summary
    description: Mapped[str] = mapped_column(Text, nullable=False)
    structured_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False) # generated, active, updated, resolved, archived
    source_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now())

class FollowUp(Base):
    __tablename__ = "follow_ups"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="scheduled", nullable=False) # scheduled, pending, completed, dismissed, overdue, escalated
    source_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now())

class PreventiveObservation(Base):
    __tablename__ = "preventive_observations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    observation_type: Mapped[str] = mapped_column(String(50), nullable=False) # missing_lab, medication_adherence, preventive_screening
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False) # active, resolved, dismissed
    structured_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now())

class ExplainabilityTrace(Base):
    __tablename__ = "explainability_traces"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    target_entity_type: Mapped[str] = mapped_column(String(50), nullable=False) # HealthInsight, PreventiveObservation, ChatResponse
    target_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    reasoning_source: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    memories_used: Mapped[Optional[list]] = mapped_column(JSON, nullable=True) # list of memory fragment IDs
    timeline_events_referenced: Mapped[Optional[list]] = mapped_column(JSON, nullable=True) # list of event descriptors
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())

class KnowledgeGap(Base):
    __tablename__ = "knowledge_gaps"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    clinical_priority: Mapped[str] = mapped_column(String(50), nullable=False)
    suggested_action: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False) # active, resolved
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())

class NextAction(Base):
    __tablename__ = "next_actions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False) # ASK_QUESTION, WAIT, REMIND, ESCALATE, REQUEST_REPORT, REQUEST_WEARABLE
    priority: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    execution_strategy: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # E.g., The question text if it's ASK_QUESTION
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False) # pending, executed, expired
    expires_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())

class UserFatigueMetrics(Base):
    __tablename__ = "user_fatigue_metrics"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False, unique=True)
    questions_asked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    questions_answered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    questions_ignored: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_response_latency_mins: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_interaction_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now())

class ClinicalOutcome(Base):
    __tablename__ = "clinical_outcomes"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    diagnosis: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    treatment_plan: Mapped[Text] = mapped_column(Text, nullable=False)
    resolved_status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    doctor_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())

class InterventionObservation(Base):
    __tablename__ = "intervention_observations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    intervention_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., "Medication: Lisinopril"
    target_metric: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., "Blood Pressure"
    baseline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    current_status: Mapped[str] = mapped_column(Text, nullable=False)
    efficacy_status: Mapped[str] = mapped_column(String(50), nullable=False) # improving, no_change, deteriorating
    evaluated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())

class CoordinatorDecision(Base):
    __tablename__ = "coordinator_decisions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    decision_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    selected_domain: Mapped[str] = mapped_column(String(100), nullable=False)
    selection_reason: Mapped[str] = mapped_column(String(100), nullable=False)
    selected_signal_ids: Mapped[list] = mapped_column(JSONB, nullable=False)
    suppressed_domains: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    checkin_count_today: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_busy_signal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    checkin_generated: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    responded_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    response_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("daily_checkins.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    __table_args__ = (UniqueConstraint("member_id", "decision_date", "selected_domain", name="uq_coordinator_member_date_domain"), Index("idx_coordinator_member_date", "member_id", "decision_date"),)

class HealthMetric(Base):
    __tablename__ = "health_metrics"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    metric_type: Mapped[str] = mapped_column(String(100), nullable=False)
    value_numeric: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    value_systolic: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    value_diastolic: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    value_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="manual")
    source_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False)
    wearable_device_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    __table_args__ = (Index("idx_metrics_member_type", "member_id", "metric_type", "recorded_at"),)

class Medication(Base):
    __tablename__ = "medications"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    generic_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dosage: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    frequency: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prescribed_by: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prescribed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    indication: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    __table_args__ = (Index("idx_medications_member_active", "member_id", "is_active"),)

class MedicationLog(Base):
    __tablename__ = "medication_logs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    medication_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("medications.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    scheduled_time: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False)
    taken_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    __table_args__ = (Index("idx_med_logs_member_date", "member_id", "scheduled_time"),)

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    original_filename: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gcs_path: Mapped[str] = mapped_column(Text, nullable=False)
    gcs_bucket: Mapped[str] = mapped_column(String(255), nullable=False, default="local")
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    processing_status: Mapped[str] = mapped_column(String(50), default="uploaded", nullable=False)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    structured_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    document_date_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    duplicate_of_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    issued_by: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    memory_ingested: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    memory_ingested_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    __table_args__ = (Index("idx_documents_member_type", "member_id", "document_type", "created_at"), Index("idx_documents_processing", "processing_status", "created_at"),)

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    condition_name: Mapped[str] = mapped_column(Text, nullable=False)
    icd_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    diagnosis_type: Mapped[str] = mapped_column(String(100), nullable=False)
    diagnosed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    diagnosed_by: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(100), default="active", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    source_consultation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    __table_args__ = (Index("idx_diagnoses_member", "member_id", "status"),)

class EscalationEvent(Base):
    __tablename__ = "escalation_events"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    triggering_signals: Mapped[dict] = mapped_column(JSONB, nullable=False)
    convergence_score: Mapped[float] = mapped_column(Float, nullable=False)
    recommended_specialty: Mapped[str] = mapped_column(String(200), nullable=False)
    escalation_reason: Mapped[str] = mapped_column(Text, nullable=False)
    urgency_level: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    consultation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    dismissed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    dismissed_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    __table_args__ = (Index("idx_escalations_member", "member_id", "triggered_at"), Index("idx_escalations_pending", "family_id", "status"),)

class Consultation(Base):
    __tablename__ = "consultations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    escalation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    consultation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    specialty: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    doctor_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    doctor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="scheduled", nullable=False)
    ai_brief: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_brief_generated_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    consultation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    follow_up_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    __table_args__ = (Index("idx_consultations_member", "member_id", "scheduled_at"),)

class MemoryOperation(Base):
    __tablename__ = "memory_operations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_entity_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    cognee_memory_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="success", nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    __table_args__ = (Index("idx_memory_ops_family", "family_id", "created_at"), Index("idx_memory_ops_entity", "source_entity_type", "source_entity_id"),)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False)
    target_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(200), nullable=False)
    resource: Mapped[str] = mapped_column(String(255), nullable=False)
    result: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    __table_args__ = (Index("idx_audit_actor", "actor_id", "timestamp"),)

class DataGrant(Base):
    __tablename__ = "data_grants"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    grantor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    grantee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    scope: Mapped[str] = mapped_column(String(100), nullable=False)
    permissions: Mapped[str] = mapped_column(String(100), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMPTZ, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    __table_args__ = (Index("idx_grants_grantee", "grantee_id"), Index("idx_grants_grantor", "grantor_id"),)

class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now())
    __table_args__ = (Index("idx_conversations_member", "member_id", "updated_at"),)

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())
    __table_args__ = (Index("idx_messages_conversation", "conversation_id", "created_at"),)
