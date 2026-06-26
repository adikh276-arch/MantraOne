from enum import Enum

class WatcherDomain(str, Enum):
    SLEEP = "sleep"
    MOOD = "mood"
    EXERCISE = "exercise"
    MEDICATION = "medication"
    NUTRITION = "nutrition"
    STRESS = "stress"
    FAMILY_CARE = "family_care"
    WOMENS_HEALTH = "womens_health"
    CHILD_HEALTH = "child_health"
    RELATIONSHIP = "relationship"

class SignalSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    @property
    def numeric_value(self) -> int:
        return {"low": 1, "medium": 2, "high": 3, "critical": 4}[self.value]
    
    def __gt__(self, other: object) -> bool:
        if not isinstance(other, SignalSeverity):
            return NotImplemented
        return self.numeric_value > other.numeric_value
    
    def __ge__(self, other: object) -> bool:
        if not isinstance(other, SignalSeverity):
            return NotImplemented
        return self.numeric_value >= other.numeric_value

class SignalType(str, Enum):
    PATTERN_CONFIRMED = "pattern_confirmed"
    TREND_CHANGE = "trend_change"
    URGENCY = "urgency"
    ROUTINE = "routine"

class TrendDirection(str, Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"

class MemoryType(str, Enum):
    DAILY_CHECKIN = "daily_checkin"
    HEALTH_METRIC = "health_metric"
    MEDICATION_LOG = "medication_log"
    DOCUMENT = "document"
    NARRATIVE = "narrative"
    CONSULTATION = "consultation"

class HealthEventType(str, Enum):
    CHECKIN_SUBMITTED = "checkin.submitted"
    HEALTH_METRIC_RECORDED = "health_metric.recorded"
    MEDICATION_LOGGED = "medication.logged"
    DOCUMENT_PROCESSED = "document.processed"
    WATCHER_SIGNAL_EMITTED = "watcher_signal.emitted"
    COORDINATOR_DECIDED = "coordinator.decided"
    ESCALATION_TRIGGERED = "escalation.triggered"
    MEMORY_INGESTED = "memory.ingested"
    DOCUMENT_UPLOADED = "document.uploaded"
    DOCUMENT_EXTRACTED = "document.extracted"

class MetricType(str, Enum):
    BLOOD_PRESSURE = "blood_pressure"
    GLUCOSE = "glucose"
    WEIGHT = "weight"
    STEPS = "steps"
    HEART_RATE = "heart_rate"
    SLEEP_DURATION = "sleep_duration"
    SLEEP_QUALITY = "sleep_quality"
    SLEEP_START = "sleep_start"
    SLEEP_END = "sleep_end"
    OXYGEN_SATURATION = "oxygen_saturation"
    TEMPERATURE = "temperature"
    HBA1C = "hba1c"
    CHOLESTEROL = "cholesterol"
    BMI = "bmi"
    CALORIES = "calories"
    WATER_INTAKE = "water_intake"
    MOOD_SCORE = "mood_score"

class MedicationStatus(str, Enum):
    TAKEN = "taken"
    MISSED = "missed"
    SKIPPED = "skipped"
    PENDING = "pending"

class DocumentType(str, Enum):
    LAB_REPORT = "lab_report"
    PRESCRIPTION = "prescription"
    MEDICAL_NOTE = "medical_note"
    SCAN = "scan"

class DocumentProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"

class ConsultationType(str, Enum):
    GP = "gp"
    SPECIALIST = "specialist"
    WELLNESS = "wellness"

class UrgencyLevel(str, Enum):
    ROUTINE = "routine"
    SOON = "soon"
    URGENT = "urgent"
    CRITICAL = "critical"

class EscalationStatus(str, Enum):
    PENDING = "pending"
    CONSULTATION_CREATED = "consultation_created"
    DISMISSED = "dismissed"

class MemberRelationship(str, Enum):
    SELF = "self"
    SPOUSE = "spouse"
    PARENT = "parent"
    CHILD = "child"
    OTHER = "other"

class SelectionReason(str, Enum):
    URGENCY = "urgency"
    TREND_CHANGE = "trend_change"
    PATTERN_CONFIRMATION = "pattern_confirmation"
    ROUTINE = "routine"

class ActorRole(str, Enum):
    MEMBER = "member"
    ADMIN = "admin"
    WORKER = "worker"
    SYSTEM = "system"

class MemoryOperationType(str, Enum):
    REMEMBER = "remember"
    RECALL = "recall"
    FORGET = "forget"
    GRAPH_QUERY = "graph_query"

class DiagnosisType(str, Enum):
    CHRONIC = "chronic"
    ACUTE = "acute"
    HISTORICAL = "historical"

class DiagnosisStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    MANAGED = "managed"

SIGNAL_TYPE_RANK: dict[SignalType, int] = {
    SignalType.URGENCY: 4,
    SignalType.TREND_CHANGE: 3,
    SignalType.PATTERN_CONFIRMED: 2,
    SignalType.ROUTINE: 1,
}
