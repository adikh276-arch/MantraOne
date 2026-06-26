# MantraOne — Antigravity Backend Build Prompt v2

> **READ THIS FIRST.** This document is the single source of truth for every Antigravity agent working on MantraOne. It is a hybrid engineering constitution, AGENTS.md, architecture decision record, and implementation roadmap. Every agent must read this document in full before writing a single line of code. No section is optional. No clarification is needed beyond what is written here.

---

## The Mission

Every healthcare interaction today starts from zero.

Every doctor asks the same questions.

Every AI forgets yesterday.

Every report becomes another PDF.

Every prescription gets buried in WhatsApp.

MantraOne exists to ensure that no family ever has to rebuild their health story again.

Every interaction becomes memory.

Every memory becomes context.

Every context becomes better care.

That is the company.

Every engineering decision should strengthen this principle.

If a feature does not strengthen longitudinal family memory,
question whether it belongs.

---

## What MantraOne Is — and Is Not

MantraOne is **NOT**

❌ AI Doctor

❌ Chatbot

❌ Medical Records

❌ Appointment Booking

❌ Symptom Checker

❌ Telemedicine App

It **IS**

✅ Persistent Family Memory

✅ Context Engine

✅ Longitudinal Health Graph

✅ Daily Companion

✅ Intelligent Follow-up

✅ Health Operating System

This definition prevents AI drift. Every agent must return to these lines when uncertain about whether a feature belongs.

---

## Product Principles

Every feature should answer:

- Does this help the AI remember?
- Does this help the AI understand?
- Does this help the AI notice?
- Does this help the AI follow up?
- Does this help the family?

If the answer is no to all five, don't build it.

---

## AI Principles

The AI should never feel

❌ Robotic

❌ Transactional

❌ Clinical

❌ Overbearing

❌ Chatty

❌ Alarmist

Instead it should feel

✅ Calm

✅ Warm

✅ Attentive

✅ Observant

✅ Reassuring

✅ Like an excellent family doctor who has known you for years

This influences every future prompt, every generated question, every escalation message, and every consultation brief.

---

## Product Constraints

If any architecture makes the product harder to understand, it is wrong.

Users should never need to know about:

- Graphs
- Embeddings
- LLMs
- Cognee
- RAG
- Vector search
- AI terminology of any kind

Everything should feel like:

> "My family has someone keeping track."

Nothing else.

---

## Architecture Principles

```
Simple      > Clever
Explicit    > Implicit
Readable    > Compact
Composition > Inheritance
Interfaces  > Concrete coupling
Domain      > Framework
Memory      > Chat
Long-term   > Short-term
Consistency > Speed
Product     > Technology
```

Every architectural decision returns to these lines.

---

## Performance Philosophy

Fast is a feature.

If an endpoint exceeds **300ms**, question the architecture — not just the query.

Users should feel **instant**.

Background jobs exist so foreground interactions remain effortless. Every heavy operation — narrative building, Cognee ingestion, Watcher evaluation, document parsing — happens asynchronously, in the background, after the API has already responded.

The foreground is for the user. The background is for the machine.

---

## What You Are Building

MantraOne is the **memory layer for an Indian family's health**. It is not a chatbot, not an EHR, not a symptom checker, and not an appointment platform. It is a continuously evolving longitudinal health intelligence system that watches, remembers, and follows up across a family's entire health journey — compounding understanding over months and years.

The product is built on **four architectural layers** defined in the PRD:

1. **Watchers** — 10 domain-specific, always-on background observers. Each owns one domain. None talks to users.
2. **Coordinator** — Picks ONE signal to surface each day. Enforces restraint. Prevents notification fatigue.
3. **Narrative Memory** — The moat. Converts raw health data into longitudinal health understanding using Cognee's graph engine.
4. **Escalation Engine** — Triggers doctor consultations on multi-Watcher convergence, not single data points.

**You are building the backend only.** No frontend, no UI components, no HTML, no CSS. When this document says "build X," it means the FastAPI routes, services, repositories, workers, database migrations, and Cognee integrations that power X. The frontend will be built separately.

---

## Event Bus Architecture

The four layers communicate through a **Health Event Bus**, not direct calls. This decouples Watchers, the Coordinator, Memory, and Escalation from each other and makes the system dramatically easier to scale and extend.

```
Health Event
     ↓
 Event Bus
     ↓
  Watchers   (subscribe to health data events, emit WatcherSignal events)
     ↓
Coordinator  (subscribes to WatcherSignal events, emits CoordinatorDecision events)
     ↓
  Memory     (subscribes to CoordinatorDecision and raw data events, ingests to Cognee)
     ↓
Escalation   (subscribes to multi-domain WatcherSignal events, emits EscalationEvent)
```

**Event types**:

```python
class HealthEventType(str, Enum):
    CHECKIN_SUBMITTED       = "checkin.submitted"
    HEALTH_METRIC_RECORDED  = "health_metric.recorded"
    MEDICATION_LOGGED       = "medication.logged"
    DOCUMENT_PROCESSED      = "document.processed"
    WATCHER_SIGNAL_EMITTED  = "watcher_signal.emitted"
    COORDINATOR_DECIDED     = "coordinator.decided"
    ESCALATION_TRIGGERED    = "escalation.triggered"
    MEMORY_INGESTED         = "memory.ingested"
```

Events are published to Redis Streams and consumed by ARQ workers. This replaces direct service-to-service calls throughout the worker layer. The API layer publishes events; it never calls workers directly.

---

## AGENTS.md — Rules Every Agent Must Follow

These rules are non-negotiable. Any code that violates them must be refactored before it is considered done.

### Architecture Rules

```
RULE-001: Never call Cognee directly from a router, service, or repository.
          All Cognee interactions MUST go through MemoryProvider or RetrievalService.

RULE-002: No business logic in routers. Routers call services. Services contain logic.
          Repositories handle database access. This boundary is absolute.

RULE-003: Family is the tenant. Every database query involving health data MUST filter
          by family_id. PostgreSQL Row Level Security enforces this at the DB layer.
          Application layer must also enforce it explicitly — defense in depth.

RULE-004: Never log raw health information. Log events and IDs only.
          WRONG: logger.info(f"User reported symptom: {symptom_description}")
          RIGHT:  logger.info(f"symptom_recorded", extra={"member_id": str(member_id)})

RULE-005: Every Watcher runs as an isolated background worker. Watchers never call
          each other. Only the Coordinator reads Watcher outputs.

RULE-006: The Escalation Engine never acts on a single Watcher signal. Escalation
          requires convergence from at least 2 Watchers over a defined time window.

RULE-007: No placeholder implementations. No TODOs in merged code. Every function
          must be complete and tested before it is considered done.

RULE-008: Every database operation must use the repository pattern.
          No raw SQLAlchemy sessions outside repository classes.

RULE-009: All secrets come from Google Secret Manager. No .env files in production.
          No secrets in code. No secrets in logs.

RULE-010: Every background worker must be idempotent. If it runs twice with the same
          input, the result must be identical. Use idempotency keys for all operations.

RULE-011: All inter-layer communication in the worker layer goes through the Event Bus.
          Workers publish events. Workers subscribe to events. No direct calls.
```

### Cognee Integration Philosophy

We are **NOT** building on top of Cognee.

We are building **WITH** Cognee.

Cognee is a core subsystem, not an implementation detail.

Whenever there is a choice between adding another database vs. using Cognee's graph and memory correctly, **prefer Cognee**.

The goal is to demonstrate deep, production-grade usage of Cognee — not to use it as a bolt-on.

```python
# The ONLY correct way to interact with Cognee is through MemoryProvider.
# No other file in this codebase may import cognee directly.

from core.providers.memory_provider import MemoryProvider

# Remember: add health data to longitudinal memory
await memory_provider.remember(
    content=narrative_text,
    metadata=HealthMemoryMetadata(
        family_id=family_id,
        member_id=member_id,
        memory_type=MemoryType.DAILY_CHECKIN,
        watcher_domains=["sleep", "mood"],
        timestamp=event_timestamp,
    )
)

# Recall: semantic search over longitudinal memory
results = await memory_provider.recall(
    query="sleep patterns over the last month",
    family_id=family_id,
    member_id=member_id,
    limit=10,
)

# Graph query: retrieve relationships
context = await memory_provider.get_health_context(
    member_id=member_id,
    include_domains=["sleep", "medication", "mood"],
    lookback_days=30,
)

# Forget: GDPR/privacy deletion
await memory_provider.forget(
    family_id=family_id,
    member_id=member_id,  # None = forget entire family
    before_date=deletion_date,  # None = forget all
)
```

### Ponytail Protocol

Ponytail is always running.

Every major implementation phase ends with a Ponytail review.

No feature is complete until Ponytail has:

- Simplified the code
- Removed duplication
- Improved naming
- Reduced complexity
- Enforced layer boundaries
- Improved readability

Ponytail runs as a pre-commit hook and as a CI step. A Ponytail error blocks the CI pipeline. There are no exceptions.

### Folder Ownership Rules

```
/api/routers/           → HTTP concerns only. Auth, request parsing, response shaping.
/core/providers/        → External service wrappers. MemoryProvider owns all Cognee.
/core/services/         → Business logic. Watcher logic, Coordinator, Escalation.
/core/repositories/     → Database access. SQLAlchemy models and queries.
/core/domain/           → Pure Python domain models. No database dependencies.
/core/workers/          → Background tasks. Watcher implementations, Coordinator loop.
/core/events/           → Event Bus. Event types, publisher, subscriber base classes.
/infrastructure/        → Database sessions, cache clients, cloud clients.
/config/                → Settings, environment loading, dependency injection.
/docs/decisions/        → Architecture Decision Records (ADRs). One per major decision.
/tests/                 → Unit, integration, and contract tests.
```

### PHI Handling Rules

```
PHI-001: Protected Health Information (PHI) includes: symptoms, diagnoses, medications,
         lab results, consultation notes, mood data, sleep data, vitals, and any
         combination of these with a person's identity.

PHI-002: PHI fields in the database must use application-level encryption before storage.
         Use the EncryptionService to encrypt/decrypt. Never store raw PHI in plaintext.

PHI-003: PHI must never appear in: URL paths, query strings, log messages, error messages,
         Redis keys, or any externally observable surface.

PHI-004: File uploads (PDFs, images) must be scanned, stored in Cloud Storage with
         private ACLs, and referenced only by a UUID. The UUID is what flows through
         the system.

PHI-005: Audit logs must capture every PHI access event: who accessed it, when,
         from which endpoint, and with what result. Use the AuditService for all
         PHI-touching operations.
```

### Testing Requirements

```
TEST-001: Every service must have unit tests with at least 80% branch coverage.
TEST-002: Every router must have integration tests covering happy path, auth failure,
          validation failure, and not-found cases.
TEST-003: Every Watcher must have a unit test that verifies it produces the correct
          WatcherSignal given known input data.
TEST-004: Every memory operation (remember, recall, forget) must have an integration
          test that verifies Cognee state before and after.
TEST-005: Escalation logic must be tested with multi-Watcher convergence scenarios.
TEST-006: No test may use production credentials. All external services must be mocked.
TEST-007: Every Event Bus subscriber must be tested in isolation with mock events.
```

### Review Checklist (Ponytail + Human)

Before any code is considered complete, verify:

- [ ] No direct Cognee calls outside `MemoryProvider` or `RetrievalService`
- [ ] No business logic in routers
- [ ] All PHI fields encrypted in database models
- [ ] No raw health data in log statements
- [ ] All new endpoints have authentication middleware applied
- [ ] All database queries filter by `family_id`
- [ ] Background workers are idempotent
- [ ] Unit tests written and passing
- [ ] No TODOs or placeholder implementations
- [ ] Migration file created for any schema changes
- [ ] API response schema defined in Pydantic v2
- [ ] New events published and consumed via Event Bus, not direct calls
- [ ] Ponytail review completed and all errors resolved
- [ ] ADR created if a significant architectural decision was made

---

## Technology Stack

### Fixed Choices — Do Not Deviate

| Layer | Technology | Notes |
|-------|-----------|-------|
| Runtime | Python 3.12 | Use `uv` for package management |
| API Framework | FastAPI 0.115+ | Async everywhere |
| Database | PostgreSQL 16 | Via Cloud SQL on Google Cloud |
| ORM | SQLAlchemy 2.0 | Async sessions, mapped_column |
| Migrations | Alembic | One migration per feature |
| Cache / Broker | Redis 7 | Via Cloud Memorystore |
| Event Bus | Redis Streams | Via existing Redis instance |
| Memory Engine | Cognee (open source) | Clone from github.com/topoteretes/cognee |
| Authentication | Firebase Auth | ID tokens verified server-side |
| Object Storage | Google Cloud Storage | Private buckets, signed URLs |
| LLM | Vertex AI (Gemini Pro) | With OpenAI fallback |
| Embeddings | Vertex AI text-embedding | With OpenAI fallback |
| Containerization | Docker + Docker Compose | Dev and CI |
| Deployment | Cloud Run | Separate services for API and workers |
| Secrets | Google Secret Manager | No .env in production |
| Observability | OpenTelemetry → Cloud Monitoring | Traces, metrics, logs |
| Task Queue | Redis + ARQ | Background workers |
| Testing | pytest + pytest-asyncio | Coverage via pytest-cov |
| Code Quality | Ponytail | Permanent architectural reviewer |

---

## Architecture Decision Records (ADRs)

Every significant architectural decision must be recorded in `docs/decisions/`. ADRs are permanent. They are never deleted — only superseded.

Initial ADR set to create at project start:

```
docs/
  decisions/
    0001-memory-provider.md       ← Why all Cognee access flows through MemoryProvider
    0002-family-tenancy.md        ← Why family_id is the tenant, not user_id
    0003-watchers.md              ← Why Watchers are isolated workers, not services
    0004-cognee.md                ← Why Cognee is a core subsystem, not a plugin
    0005-security.md              ← PHI encryption strategy and RLS rationale
    0006-event-bus.md             ← Why the Event Bus decouples all four layers
    0007-coordinator-restraint.md ← Why the Coordinator enforces silence as a valid output
```

ADR format:

```md
# ADR-XXXX: [Title]

## Status
Accepted | Superseded by ADR-YYYY

## Context
Why this decision was needed.

## Decision
What was decided.

## Consequences
What this enables. What it constrains.
```

---

## Repository Structure

```
mantraone-backend/
├── AGENTS.md                          ← This document (abbreviated version)
├── README.md
├── pyproject.toml                     ← uv project config
├── Dockerfile
├── Dockerfile.worker
├── docker-compose.yml                 ← Local dev: API + PostgreSQL + Redis
├── docker-compose.test.yml            ← Test environment
├── ponytail.config.yml                ← Ponytail rules
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                      ← One file per migration
│
├── docs/
│   └── decisions/                     ← ADRs. See Architecture Decision Records section.
│
├── api/
│   ├── __init__.py
│   ├── main.py                        ← FastAPI app factory
│   ├── dependencies.py                ← get_current_user, get_db, get_redis
│   ├── middleware/
│   │   ├── auth.py                    ← Firebase token verification
│   │   ├── audit.py                   ← PHI audit logging
│   │   ├── rate_limit.py              ← Redis-backed rate limiting
│   │   └── telemetry.py               ← OpenTelemetry spans
│   └── routers/
│       ├── v1/
│       │   ├── auth.py                ← POST /v1/auth/verify
│       │   ├── families.py            ← Family CRUD
│       │   ├── members.py             ← Member CRUD
│       │   ├── checkins.py            ← Daily check-ins
│       │   ├── health_records.py      ← Vitals, symptoms, medications
│       │   ├── documents.py           ← PDF/image upload and processing
│       │   ├── timeline.py            ← Health timeline retrieval
│       │   ├── memory.py              ← Semantic recall and context
│       │   ├── consultations.py       ← Doctor escalation and consultations
│       │   ├── watcher_signals.py     ← Coordinator surface decisions
│       │   └── admin.py               ← Internal admin endpoints
│       └── health.py                  ← GET /health (no auth required)
│
├── core/
│   ├── events/
│   │   ├── types.py                   ← HealthEventType enum and event schemas
│   │   ├── publisher.py               ← Publishes events to Redis Streams
│   │   └── subscriber.py              ← Base class for event subscribers/consumers
│   │
│   ├── providers/
│   │   ├── memory_provider.py         ← ALL Cognee interactions (RULE-001)
│   │   ├── retrieval_service.py       ← Cognee search and graph queries
│   │   ├── storage_provider.py        ← Cloud Storage upload/download/sign
│   │   ├── llm_provider.py            ← Vertex AI / OpenAI wrapper
│   │   └── encryption_service.py      ← PHI field encryption/decryption
│   │
│   ├── services/
│   │   ├── family_service.py
│   │   ├── member_service.py
│   │   ├── checkin_service.py
│   │   ├── health_record_service.py
│   │   ├── document_service.py        ← PDF parsing, OCR, extraction
│   │   ├── coordinator_service.py     ← Picks ONE signal per day per member
│   │   ├── escalation_service.py      ← Multi-watcher convergence logic
│   │   ├── narrative_service.py       ← Converts data to narrative for Cognee
│   │   ├── consultation_service.py    ← Doctor brief generation
│   │   ├── timeline_service.py        ← Health timeline construction
│   │   └── audit_service.py           ← PHI access audit logging
│   │
│   ├── repositories/
│   │   ├── base.py                    ← BaseRepository with family_id scoping
│   │   ├── family_repository.py
│   │   ├── member_repository.py
│   │   ├── checkin_repository.py
│   │   ├── health_record_repository.py
│   │   ├── watcher_signal_repository.py
│   │   ├── coordinator_decision_repository.py
│   │   ├── escalation_repository.py
│   │   ├── document_repository.py
│   │   ├── consultation_repository.py
│   │   └── audit_repository.py
│   │
│   ├── domain/
│   │   ├── entities.py                ← Pure Python dataclasses (no DB deps)
│   │   ├── enums.py                   ← WatcherDomain, HealthMetricType, etc.
│   │   └── value_objects.py           ← HealthBaseline, SignalSeverity, etc.
│   │
│   └── workers/
│       ├── worker_main.py             ← ARQ worker entry point
│       ├── watchers/
│       │   ├── base_watcher.py        ← Abstract Watcher interface
│       │   ├── sleep_watcher.py
│       │   ├── mood_watcher.py
│       │   ├── exercise_watcher.py
│       │   ├── medication_watcher.py
│       │   ├── nutrition_watcher.py
│       │   ├── stress_watcher.py      ← Cross-correlates mood+sleep+activity
│       │   ├── family_care_watcher.py ← Cross-family pattern detection
│       │   ├── womens_health_watcher.py
│       │   ├── child_health_watcher.py
│       │   └── relationship_watcher.py
│       ├── coordinator.py             ← Daily signal selection logic
│       ├── escalation_engine.py       ← Multi-watcher convergence evaluation
│       └── narrative_builder.py       ← Converts signals to Cognee memory
│
├── infrastructure/
│   ├── database/
│   │   ├── session.py                 ← Async SQLAlchemy session factory
│   │   ├── models.py                  ← SQLAlchemy ORM models
│   │   └── row_level_security.py      ← PostgreSQL RLS policy setup
│   ├── cache/
│   │   └── redis_client.py
│   └── cloud/
│       ├── storage.py                 ← GCS client
│       ├── secrets.py                 ← Secret Manager client
│       └── firebase.py                ← Firebase Admin SDK
│
├── config/
│   ├── settings.py                    ← Pydantic BaseSettings
│   └── dependencies.py                ← FastAPI dependency injection
│
└── tests/
    ├── conftest.py
    ├── factories/                     ← Test data factories
    ├── unit/
    │   ├── test_watchers/
    │   ├── test_services/
    │   └── test_providers/
    └── integration/
        ├── test_routers/
        └── test_memory_lifecycle/
```

---

## Database Design

### Principles

- Family is the tenant. Every health data table has a `family_id` column.
- Row Level Security (RLS) is enabled on all health data tables.
- All health data fields that contain PHI are encrypted at the application layer before storage.
- Soft deletes (`deleted_at` timestamp) on all domain tables.
- Audit trail (`created_at`, `updated_at`, `created_by`) on all tables.
- Versioning via `version` integer column with optimistic locking.

### Core Tables

#### families
```sql
CREATE TABLE families (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    primary_user_id UUID NOT NULL,           -- Firebase UID of the account owner
    subscription_tier VARCHAR(50) DEFAULT 'basic',
    subscription_valid_until TIMESTAMPTZ,
    onboarding_completed_at TIMESTAMPTZ,
    health_baseline_version INT DEFAULT 0,   -- Incremented when baseline is recalculated
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    version         INT NOT NULL DEFAULT 1
);

CREATE INDEX idx_families_primary_user ON families(primary_user_id);
```

#### family_members
```sql
CREATE TABLE family_members (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    firebase_uid    VARCHAR(255),            -- Null if member hasn't signed up yet
    name            VARCHAR(255) NOT NULL,   -- Encrypted
    date_of_birth   DATE,                    -- Encrypted
    gender          VARCHAR(50),
    relationship    VARCHAR(100) NOT NULL,   -- 'self', 'spouse', 'parent', 'child', 'other'
    is_primary      BOOLEAN DEFAULT FALSE,
    avatar_url      TEXT,
    timezone        VARCHAR(100) DEFAULT 'Asia/Kolkata',
    preferred_language VARCHAR(10) DEFAULT 'en',
    health_profile_complete BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    version         INT NOT NULL DEFAULT 1
);

CREATE INDEX idx_members_family ON family_members(family_id);
CREATE INDEX idx_members_firebase_uid ON family_members(firebase_uid);
ALTER TABLE family_members ENABLE ROW LEVEL SECURITY;
```

#### health_baselines
```sql
-- Stores the personal baseline for each member per domain.
-- The Escalation Engine compares current signals against baseline, not population averages.
CREATE TABLE health_baselines (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    member_id       UUID NOT NULL REFERENCES family_members(id),
    domain          VARCHAR(100) NOT NULL,   -- 'sleep', 'mood', 'exercise', etc.
    baseline_data   JSONB NOT NULL,          -- Domain-specific baseline metrics (encrypted)
    calculated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data_points_count INT NOT NULL DEFAULT 0,
    confidence_score FLOAT DEFAULT 0.0,      -- 0-1, increases as more data accumulates
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(member_id, domain)
);

CREATE INDEX idx_baselines_member_domain ON health_baselines(member_id, domain);
ALTER TABLE health_baselines ENABLE ROW LEVEL SECURITY;
```

#### daily_checkins
```sql
CREATE TABLE daily_checkins (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    member_id       UUID NOT NULL REFERENCES family_members(id),
    checkin_date    DATE NOT NULL,
    checkin_time    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    domain          VARCHAR(100) NOT NULL,   -- Which watcher domain this addresses
    raw_response    TEXT,                    -- Encrypted user response text
    structured_data JSONB,                   -- Parsed and structured data (encrypted)
    ai_initiated    BOOLEAN DEFAULT TRUE,    -- True if AI surfaced this, False if user-initiated
    coordinator_decision_id UUID,            -- References the decision that surfaced this
    memory_ingested BOOLEAN DEFAULT FALSE,   -- Has this been sent to Cognee?
    memory_ingested_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(member_id, checkin_date, domain)
);

CREATE INDEX idx_checkins_member_date ON daily_checkins(member_id, checkin_date DESC);
CREATE INDEX idx_checkins_family_date ON daily_checkins(family_id, checkin_date DESC);
CREATE INDEX idx_checkins_memory_pending ON daily_checkins(memory_ingested, created_at)
    WHERE memory_ingested = FALSE;
ALTER TABLE daily_checkins ENABLE ROW LEVEL SECURITY;
```

#### watcher_signals
```sql
-- Output of each Watcher run. Watchers write here. Coordinator reads from here.
CREATE TABLE watcher_signals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    member_id       UUID NOT NULL REFERENCES family_members(id),
    watcher_domain  VARCHAR(100) NOT NULL,
    signal_date     DATE NOT NULL DEFAULT CURRENT_DATE,
    signal_type     VARCHAR(100) NOT NULL,  -- 'pattern_confirmed', 'trend_change', 'urgency', 'routine'
    severity        VARCHAR(50) NOT NULL,   -- 'low', 'medium', 'high', 'critical'
    signal_payload  JSONB NOT NULL,         -- Watcher-specific signal data
    deviation_from_baseline FLOAT,         -- How much this deviates from personal baseline (-1 to 1)
    trend_direction VARCHAR(20),            -- 'improving', 'stable', 'declining', 'volatile'
    supporting_data JSONB,                  -- Evidence used to generate this signal
    surfaced        BOOLEAN DEFAULT FALSE,  -- Has Coordinator acted on this?
    surfaced_at     TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,            -- Signal relevance window
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_signals_member_domain ON watcher_signals(member_id, watcher_domain, signal_date DESC);
CREATE INDEX idx_signals_unsurfaced ON watcher_signals(family_id, surfaced, severity, created_at)
    WHERE surfaced = FALSE;
ALTER TABLE watcher_signals ENABLE ROW LEVEL SECURITY;
```

#### coordinator_decisions
```sql
-- Records every Coordinator decision: what to surface today and why.
CREATE TABLE coordinator_decisions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    member_id       UUID NOT NULL REFERENCES family_members(id),
    decision_date   DATE NOT NULL DEFAULT CURRENT_DATE,
    selected_domain VARCHAR(100) NOT NULL,
    selection_reason VARCHAR(100) NOT NULL,  -- 'urgency', 'trend_change', 'pattern_confirmation', 'routine'
    selected_signal_ids UUID[] NOT NULL,     -- Signals that informed this decision
    suppressed_domains VARCHAR(100)[],       -- Domains considered but not selected
    checkin_count_today INT DEFAULT 0,       -- Never exceed 2
    user_busy_signal BOOLEAN DEFAULT FALSE,  -- User indicated busyness → reduce frequency
    checkin_generated TEXT,                  -- The actual check-in question text (AI-generated)
    delivered_at    TIMESTAMPTZ,
    responded_at    TIMESTAMPTZ,
    response_id     UUID REFERENCES daily_checkins(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(member_id, decision_date, selected_domain)
);

CREATE INDEX idx_coordinator_member_date ON coordinator_decisions(member_id, decision_date DESC);
ALTER TABLE coordinator_decisions ENABLE ROW LEVEL SECURITY;
```

#### health_metrics
```sql
-- Vitals and measurable health data: BP, glucose, weight, steps, HR, etc.
CREATE TABLE health_metrics (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    member_id       UUID NOT NULL REFERENCES family_members(id),
    metric_type     VARCHAR(100) NOT NULL,  -- 'blood_pressure', 'glucose', 'weight', 'steps', etc.
    value_numeric   FLOAT,
    value_systolic  FLOAT,                  -- For blood pressure
    value_diastolic FLOAT,                  -- For blood pressure
    value_text      TEXT,                   -- For non-numeric metrics (encrypted)
    unit            VARCHAR(50),
    source          VARCHAR(100) NOT NULL,  -- 'manual', 'google_fit', 'apple_health', 'lab_report'
    source_document_id UUID,               -- References documents table if from lab report
    recorded_at     TIMESTAMPTZ NOT NULL,   -- When the measurement was taken
    wearable_device_id VARCHAR(255),
    notes           TEXT,                   -- Encrypted
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_metrics_member_type ON health_metrics(member_id, metric_type, recorded_at DESC);
CREATE INDEX idx_metrics_source_doc ON health_metrics(source_document_id) WHERE source_document_id IS NOT NULL;
ALTER TABLE health_metrics ENABLE ROW LEVEL SECURITY;
```

#### medications
```sql
CREATE TABLE medications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    member_id       UUID NOT NULL REFERENCES family_members(id),
    name            VARCHAR(500) NOT NULL,   -- Encrypted
    generic_name    VARCHAR(500),            -- Encrypted
    dosage          VARCHAR(200),            -- Encrypted (e.g., "500mg twice daily")
    frequency       VARCHAR(200),            -- Encrypted
    prescribed_by   VARCHAR(255),            -- Doctor name (encrypted)
    prescribed_date DATE,
    start_date      DATE NOT NULL,
    end_date        DATE,                    -- Null = ongoing
    indication      TEXT,                    -- Why it was prescribed (encrypted)
    source_document_id UUID,
    is_active       BOOLEAN DEFAULT TRUE,
    adherence_target_times TIME[],           -- Expected dose times
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_medications_member_active ON medications(member_id, is_active);
ALTER TABLE medications ENABLE ROW LEVEL SECURITY;
```

#### medication_logs
```sql
-- Medication adherence tracking. Medication Watcher reads this.
CREATE TABLE medication_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    medication_id   UUID NOT NULL REFERENCES medications(id),
    member_id       UUID NOT NULL REFERENCES family_members(id),
    scheduled_time  TIMESTAMPTZ NOT NULL,
    taken_at        TIMESTAMPTZ,            -- Null = missed or not yet due
    status          VARCHAR(50) NOT NULL,   -- 'taken', 'missed', 'skipped', 'pending'
    notes           TEXT,                   -- Encrypted
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_med_logs_member_date ON medication_logs(member_id, scheduled_time DESC);
ALTER TABLE medication_logs ENABLE ROW LEVEL SECURITY;
```

#### documents
```sql
-- Lab reports, prescriptions, medical notes, images uploaded by family.
CREATE TABLE documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    member_id       UUID NOT NULL REFERENCES family_members(id),
    document_type   VARCHAR(100) NOT NULL,   -- 'lab_report', 'prescription', 'medical_note', 'scan'
    original_filename VARCHAR(500),          -- Encrypted
    gcs_path        TEXT NOT NULL,           -- GCS object path (never a public URL)
    gcs_bucket      VARCHAR(255) NOT NULL,
    mime_type       VARCHAR(100) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    checksum_sha256 VARCHAR(64) NOT NULL,
    processing_status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'processing', 'complete', 'failed'
    extracted_text  TEXT,                    -- OCR output (encrypted)
    structured_data JSONB,                   -- Parsed structured data from document (encrypted)
    document_date   DATE,                    -- Date on the document itself
    issued_by       VARCHAR(500),            -- Hospital/lab name (encrypted)
    memory_ingested BOOLEAN DEFAULT FALSE,
    memory_ingested_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_documents_member_type ON documents(member_id, document_type, created_at DESC);
CREATE INDEX idx_documents_processing ON documents(processing_status, created_at)
    WHERE processing_status IN ('pending', 'processing');
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
```

#### diagnoses
```sql
CREATE TABLE diagnoses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    member_id       UUID NOT NULL REFERENCES family_members(id),
    condition_name  VARCHAR(500) NOT NULL,   -- Encrypted
    icd_code        VARCHAR(20),
    diagnosis_type  VARCHAR(100) NOT NULL,   -- 'chronic', 'acute', 'historical'
    diagnosed_date  DATE,
    diagnosed_by    VARCHAR(255),            -- Encrypted
    severity        VARCHAR(50),             -- 'mild', 'moderate', 'severe'
    status          VARCHAR(100) DEFAULT 'active',  -- 'active', 'resolved', 'managed'
    notes           TEXT,                    -- Encrypted
    source_document_id UUID,
    source_consultation_id UUID,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_diagnoses_member ON diagnoses(member_id, status);
ALTER TABLE diagnoses ENABLE ROW LEVEL SECURITY;
```

#### consultations
```sql
-- Doctor consultations, both AI-escalated and user-initiated.
CREATE TABLE consultations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    member_id       UUID NOT NULL REFERENCES family_members(id),
    escalation_id   UUID,                    -- References escalation_events if AI-triggered
    consultation_type VARCHAR(100) NOT NULL, -- 'gp', 'specialist', 'wellness'
    specialty       VARCHAR(200),
    doctor_name     VARCHAR(500),            -- Encrypted
    doctor_id       UUID,                    -- If doctor is in our system
    scheduled_at    TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    status          VARCHAR(50) DEFAULT 'scheduled',
    ai_brief        TEXT,                    -- AI-prepared health brief (encrypted)
    ai_brief_generated_at TIMESTAMPTZ,
    consultation_notes TEXT,                 -- Post-consultation notes (encrypted)
    follow_up_required BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_consultations_member ON consultations(member_id, scheduled_at DESC);
ALTER TABLE consultations ENABLE ROW LEVEL SECURITY;
```

#### escalation_events
```sql
-- Records every Escalation Engine decision. Requires multi-watcher convergence.
CREATE TABLE escalation_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    member_id       UUID NOT NULL REFERENCES family_members(id),
    triggered_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    triggering_signals JSONB NOT NULL,       -- Array of {domain, signal_id, severity}
    convergence_score FLOAT NOT NULL,        -- How strong the multi-watcher convergence was
    recommended_specialty VARCHAR(200) NOT NULL,
    escalation_reason TEXT NOT NULL,         -- Human-readable explanation
    urgency_level   VARCHAR(50) NOT NULL,    -- 'routine', 'soon', 'urgent'
    status          VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'consultation_created', 'dismissed'
    consultation_id UUID REFERENCES consultations(id),
    dismissed_at    TIMESTAMPTZ,
    dismissed_reason TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_escalations_member ON escalation_events(member_id, triggered_at DESC);
CREATE INDEX idx_escalations_pending ON escalation_events(family_id, status)
    WHERE status = 'pending';
ALTER TABLE escalation_events ENABLE ROW LEVEL SECURITY;
```

#### memory_operations
```sql
-- Audit trail for every Cognee memory operation.
CREATE TABLE memory_operations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID NOT NULL REFERENCES families(id),
    member_id       UUID,
    operation_type  VARCHAR(50) NOT NULL,    -- 'remember', 'recall', 'forget', 'graph_query'
    source_entity_type VARCHAR(100),         -- 'checkin', 'document', 'health_metric', etc.
    source_entity_id UUID,
    cognee_memory_id VARCHAR(255),           -- Cognee's internal ID for tracking
    status          VARCHAR(50) DEFAULT 'success',
    error_message   TEXT,
    duration_ms     INT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_memory_ops_family ON memory_operations(family_id, created_at DESC);
CREATE INDEX idx_memory_ops_entity ON memory_operations(source_entity_type, source_entity_id);
```

#### audit_logs
```sql
-- PHI access audit log. Every access to health data creates a record.
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id       UUID,
    member_id       UUID,
    actor_firebase_uid VARCHAR(255) NOT NULL,
    actor_role      VARCHAR(100) NOT NULL,   -- 'member', 'admin', 'worker', 'system'
    action          VARCHAR(200) NOT NULL,   -- 'read_health_record', 'update_checkin', etc.
    resource_type   VARCHAR(100) NOT NULL,
    resource_id     UUID,
    endpoint        VARCHAR(500),
    ip_address      VARCHAR(45),             -- IPv6 compatible
    user_agent      TEXT,
    result          VARCHAR(50) NOT NULL,    -- 'success', 'denied', 'error'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);
-- Create monthly partitions for audit logs
CREATE TABLE audit_logs_2026_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
-- (Alembic migration will generate all 12 months + automation for new months)

CREATE INDEX idx_audit_family ON audit_logs(family_id, created_at DESC);
CREATE INDEX idx_audit_actor ON audit_logs(actor_firebase_uid, created_at DESC);
```

---

## The Four Core Layers — Implementation Specification

### Layer 1: Watchers

Each Watcher is an ARQ background job that runs on a schedule. They share a common interface.

```python
# core/workers/watchers/base_watcher.py

class BaseWatcher(ABC):
    domain: WatcherDomain  # Must be defined by each subclass

    @abstractmethod
    async def evaluate(
        self,
        member: FamilyMember,
        lookback_window: timedelta,
        db: AsyncSession,
        redis: Redis,
    ) -> WatcherSignal | None:
        """
        Analyze recent data for this member and domain.
        Returns a WatcherSignal if something worth noting is detected.
        Returns None if everything is within normal range.
        MUST be idempotent — safe to call multiple times with same input.
        MUST NOT communicate with the user directly.
        MUST NOT call other Watchers.
        MUST NOT call LLM APIs — Watchers do statistical analysis only.
        On completion, publishes a WATCHER_SIGNAL_EMITTED event to the Event Bus.
        """

    async def calculate_baseline_deviation(
        self,
        current_value: float,
        member_id: UUID,
        domain: WatcherDomain,
        db: AsyncSession,
    ) -> float:
        """
        Returns deviation from personal baseline (-1.0 to 1.0).
        Uses health_baselines table. Falls back to 0.0 if no baseline exists yet.
        """
```

**Watcher Schedule**: Each Watcher evaluates once per hour per active member. The ARQ worker pool runs 4 parallel workers. Total evaluation time budget per member per Watcher: 30 seconds.

**Sleep Watcher specifics**: Reads from `health_metrics` where `metric_type IN ('sleep_duration', 'sleep_quality', 'sleep_start', 'sleep_end')`. Calculates 7-day rolling average, detects Sunday-night patterns, pre-event disruptions.

**Stress Watcher specifics**: The Stress Watcher is the only Watcher that reads outputs from other Watchers (via `watcher_signals` table). It cross-correlates Sleep + Mood + Exercise signals to produce a composite stress score.

**Family Care Watcher specifics**: This is a family-level Watcher. It evaluates all members in a family and detects cross-family patterns (e.g., "two members both reporting poor sleep this week").

### Layer 2: Coordinator

The Coordinator runs once per member per day (6 AM IST by default). It subscribes to `WATCHER_SIGNAL_EMITTED` events and is also triggered by its daily schedule.

```
CoordinatorService.select_daily_signal(member_id) must:

1. Load all unsurfaced WatcherSignals from the last 48 hours.
2. Check checkin_count_today — if already 2, return None (no more today).
3. Check user_busy_signal — if True, only surface urgency-level signals.
4. Rank signals by: URGENCY > TREND_CHANGE > PATTERN_CONFIRMATION > ROUTINE
5. Select the highest-ranked signal.
6. Generate a check-in question using LLM that:
   - References why it's surfacing ("You mentioned...", "Your data shows...")
   - Never surprises the user — always grounded in something they shared
   - Is conversational, warm, not clinical
7. Create a CoordinatorDecision record.
8. Mark the selected WatcherSignals as surfaced.
9. Publish a COORDINATOR_DECIDED event to the Event Bus.
10. Return the generated check-in text.
```

**Restraint Rules (must be enforced in code, not just documentation)**:
- Maximum 2 check-ins per member per day. Hard limit enforced in `coordinator_decisions` table.
- If `user_busy_signal` is True, skip routine and pattern-confirmation signals for 48 hours.
- Silence is valid. If no signal warrants surfacing, the Coordinator returns None and publishes nothing.

### Layer 3: Narrative Memory (via Cognee)

The `NarrativeBuilder` worker subscribes to `CHECKIN_SUBMITTED`, `HEALTH_METRIC_RECORDED`, `MEDICATION_LOGGED`, and `DOCUMENT_PROCESSED` events.

```python
# core/workers/narrative_builder.py

async def build_narrative_and_remember(
    source_type: str,  # 'checkin', 'document', 'health_metric'
    source_id: UUID,
    member_id: UUID,
    family_id: UUID,
    db: AsyncSession,
    memory_provider: MemoryProvider,
) -> None:
    """
    1. Load the source entity from the database.
    2. Construct a rich narrative text that includes:
       - The data point itself
       - Context from recent related data
       - The member's personal baseline for comparison
       - Temporal context ("three weeks ago you started...")
    3. Call memory_provider.remember() with the narrative + metadata.
    4. Update the source entity's memory_ingested = True.
    5. Log to memory_operations table.
    6. Publish a MEMORY_INGESTED event to the Event Bus.

    Example narrative for a sleep check-in:
    "On 2026-06-26, Priya reported sleeping 4h 22m. This is the third consecutive
    night below 5 hours this week. Her 30-day baseline sleep duration is 6h 45m.
    She previously mentioned knee pain on 2026-06-21. Her resting heart rate has
    been 2 bpm above her baseline this week."
    """
```

The narrative format is the critical element. Raw data goes in; rich contextual understanding comes out. This is what makes Cognee's graph useful — not just storing facts, but storing facts in context.

### Layer 4: Escalation Engine

The Escalation Engine subscribes to `WATCHER_SIGNAL_EMITTED` events and evaluates convergence after each new signal.

```python
# core/workers/escalation_engine.py

ESCALATION_THRESHOLD_CONFIG = {
    # Format: (min_watchers_involved, min_severity_for_any, min_convergence_duration_days)
    "routine": (2, "medium", 7),   # 2+ watchers at medium+ severity over 7 days
    "soon":    (2, "high", 3),     # 2+ watchers at high+ severity over 3 days
    "urgent":  (2, "high", 1),     # 2+ watchers at high+ severity in same day
    "critical":(1, "critical", 0), # Any single critical signal = immediate escalation
}

async def evaluate_escalation(
    member_id: UUID,
    family_id: UUID,
    db: AsyncSession,
) -> EscalationEvent | None:
    """
    Load recent WatcherSignals across all domains.
    Apply threshold config to detect convergence.
    If convergence detected and no escalation created in last 7 days for same signals:
        - Determine recommended specialty based on signal domains
        - Generate escalation reason using LLM
        - Create EscalationEvent record
        - Create pending Consultation record with AI brief
        - Publish ESCALATION_TRIGGERED event to the Event Bus
    Return the EscalationEvent if created, else None.
    """
```

**Specialty mapping** (signal domains → recommended specialty):
- sleep + mood + stress → General Physician or Mental Health
- glucose + diet + stress → Diabetologist
- child symptoms + no consultation in 60 days → Paediatrician
- BP + stress + medication miss → General Physician
- women's health signals → Women's Wellness or Gynaecologist

---

## API Design — Tiered Priority

### Tier 1: Core (build first, agents can parallelize)

#### POST /v1/auth/verify
- Verifies a Firebase ID token server-side
- Creates or updates the family member's Firebase UID linkage
- Returns: `{ member_id, family_id, is_onboarded }`
- No auth middleware required (this is the auth entry point)

#### POST /v1/families
- Creates a new family with the authenticated user as primary member
- Body: `{ name: str }`
- Response: `FamilyResponse`
- Background: creates default health baseline records for all Watcher domains

#### GET /v1/families/me
- Returns the authenticated user's family with all members
- Auth: Firebase ID token → family_id
- Response: `FamilyWithMembersResponse`

#### POST /v1/families/{family_id}/members
- Adds a new family member (not yet a Firebase user — can be added by name/relationship)
- Body: `{ name, date_of_birth, gender, relationship }`
- Auth: must be primary member of the family
- Response: `MemberResponse`

#### POST /v1/checkins
- Submits a daily check-in response from the user
- Body: `{ coordinator_decision_id, response_text, structured_data? }`
- Auth: Firebase ID token → member_id
- Publishes: `CHECKIN_SUBMITTED` event → NarrativeBuilder and Watcher re-evaluation pick it up
- Response: `CheckinResponse`

#### GET /v1/checkins/today
- Returns the Coordinator's selected signal for today and the generated check-in question
- Auth: Firebase ID token → member_id
- Calls `CoordinatorService.select_daily_signal()` if not already decided today
- Response: `{ question: str, domain: str, coordinator_decision_id: uuid, context: str }`

#### POST /v1/health-metrics
- Records a health measurement (BP, glucose, steps, weight, etc.)
- Body: `{ metric_type, value_numeric?, value_systolic?, value_diastolic?, unit, recorded_at, source, notes? }`
- Publishes: `HEALTH_METRIC_RECORDED` event → Watcher re-evaluation and NarrativeBuilder pick it up
- Response: `HealthMetricResponse`

#### POST /v1/medications
- Adds a medication to a member's record
- Body: `{ name, dosage, frequency, start_date, prescribed_by?, indication? }`
- Response: `MedicationResponse`

#### POST /v1/medications/{medication_id}/logs
- Logs a medication dose (taken, missed, or skipped)
- Body: `{ status, taken_at?, notes? }`
- Publishes: `MEDICATION_LOGGED` event → Medication Watcher re-evaluation picks it up
- Response: `MedicationLogResponse`

### Tier 2: Dependent on Tier 1

#### POST /v1/documents
- Uploads a PDF or image document (lab report, prescription, medical note)
- Multipart form: `{ file, document_type, member_id, document_date? }`
- Validates: max 20MB, allowed MIME types
- Uploads to GCS immediately with UUID path, never original filename
- Publishes: document processing pipeline initiated via Event Bus
- Response: `{ document_id, status: "processing" }`

#### GET /v1/documents/{document_id}
- Returns document metadata and signed URL valid for 15 minutes
- Auth: must be member of the family that owns the document
- PHI audit log created on every access

#### GET /v1/members/{member_id}/timeline
- Returns the health timeline for a member: ordered list of significant events
- Query params: `?start_date=&end_date=&domains[]=`
- Calls `TimelineService.build_timeline()` which queries across all health tables
- Response: `TimelineResponse` with events ordered chronologically

#### GET /v1/members/{member_id}/memory
- Semantic recall from Narrative Memory
- Query params: `?q=your query here&limit=10`
- Calls `RetrievalService.recall()` which queries Cognee
- Returns: relevant memory fragments with confidence scores and timestamps
- Auth: PHI audit log created

#### GET /v1/members/{member_id}/context
- Returns the full health context for a member for a given domain and time window
- Used internally by the AI brief generator and externally by the chat layer
- Query params: `?domains[]=&lookback_days=30`
- Calls `memory_provider.get_health_context()`
- Response: `HealthContextResponse`

#### POST /v1/escalations/{escalation_id}/consultations
- Converts a pending escalation into a consultation booking
- Body: `{ preferred_time_slots[], notes? }`
- Background: generates AI doctor brief using `ConsultationService.generate_brief()`
- Response: `ConsultationResponse`

#### GET /v1/consultations/{consultation_id}/brief
- Returns the AI-prepared health brief for a consultation
- This is what the doctor sees before the call
- Auth: must be family member or authenticated doctor
- PHI audit log created

### Tier 3: Enhancement (build last)

#### GET /v1/members/{member_id}/watcher-signals
- Internal/admin: view raw Watcher output for debugging
- Auth: admin only or primary family member

#### DELETE /v1/members/{member_id}/memory
- Deletes a member's longitudinal memory from Cognee
- Calls `memory_provider.forget(member_id=member_id)`
- Also soft-deletes all health data for this member in PostgreSQL
- Creates GDPR deletion record

#### DELETE /v1/families/{family_id}/memory
- Deletes an entire family's data (account closure)
- Calls `memory_provider.forget(family_id=family_id, member_id=None)`
- Cascades to all members

#### GET /v1/admin/escalation-stats
- Admin dashboard endpoint: escalation rates by domain, specialty distribution
- Auth: admin JWT only

#### GET /health
- No auth. Returns `{ status: "ok", version: "1.x.x" }`. Used by Cloud Run health checks.

---

## MemoryProvider — Complete Specification

This is the most important file in the codebase. Every Cognee interaction flows through here.

```python
# core/providers/memory_provider.py

class HealthMemoryMetadata(BaseModel):
    family_id: UUID
    member_id: UUID
    memory_type: MemoryType
    watcher_domains: list[str]
    timestamp: datetime
    source_entity_type: str
    source_entity_id: UUID
    confidence: float = 1.0

class MemoryProvider:
    """
    The ONLY interface to Cognee in this codebase.
    Wraps all cognee operations with:
    - Family-scoped namespacing (all Cognee datasets are prefixed with family_id)
    - Metadata enrichment
    - Error handling and retry
    - Audit logging to memory_operations table
    - PHI compliance (never pass raw field values in metadata keys visible outside)
    """

    async def remember(
        self,
        content: str,                    # The narrative text to memorize
        metadata: HealthMemoryMetadata,
    ) -> str:
        """
        Ingests content into Cognee's memory graph.
        Sets Cognee's dataset to f"family_{family_id}_member_{member_id}".
        Calls cognee.add() then cognee.cognify().
        Logs to memory_operations.
        Returns Cognee's memory ID.
        """

    async def recall(
        self,
        query: str,
        family_id: UUID,
        member_id: UUID,
        limit: int = 10,
        min_confidence: float = 0.5,
    ) -> list[MemoryFragment]:
        """
        Semantic search over a member's longitudinal memory.
        Uses cognee.search() with SIMILARITY mode.
        Filters by family/member namespace.
        Returns ordered list of MemoryFragments with content and score.
        """

    async def get_health_context(
        self,
        member_id: UUID,
        include_domains: list[str],
        lookback_days: int = 30,
    ) -> HealthContext:
        """
        Graph-based context retrieval.
        Uses cognee.search() with GRAPH_COMPLETION mode.
        Returns structured HealthContext with entity relationships.
        This is what the AI brief generator and Coordinator use.
        """

    async def forget(
        self,
        family_id: UUID,
        member_id: UUID | None = None,
        before_date: datetime | None = None,
    ) -> ForgetResult:
        """
        Deletes memory from Cognee's graph.
        If member_id is None, deletes entire family namespace.
        If before_date is set, only deletes memories older than that date.
        Creates memory_operations record with operation_type='forget'.
        """
```

---

## Document Processing Pipeline

When a document is uploaded, it goes through this pipeline as a series of events on the Event Bus:

```
1. document_upload_task (immediate, triggered by POST /v1/documents)
   → Validates file integrity (checksum)
   → Stores in GCS at: {family_id}/{member_id}/{document_type}/{uuid}.{ext}
   → Creates document record with status='pending'
   → Publishes: document.uploaded event

2. document_extract_task (subscribes to document.uploaded)
   → OCR via Cloud Vision API for images/scanned PDFs
   → Text extraction via pdfplumber for digital PDFs
   → Stores extracted_text in document record (encrypted)
   → Publishes: document.extracted event

3. document_parse_task (subscribes to document.extracted)
   → LLM call to structure the extracted text into known fields
   → For lab reports: extract test_name, value, unit, reference_range, date
   → For prescriptions: extract medication_name, dosage, frequency, duration
   → For medical notes: extract symptoms, diagnosis, recommendations
   → Creates health_metrics, medications, or diagnoses records from parsed data
   → Updates document.structured_data
   → Publishes: DOCUMENT_PROCESSED event

4. document_ingest_task (subscribes to DOCUMENT_PROCESSED)
   → Calls NarrativeBuilder with the structured document data
   → Ingests rich narrative into Cognee memory
   → Updates document.memory_ingested = True
   → Triggers Watcher re-evaluation for affected domains via Event Bus
```

---

## Ponytail Configuration

```yaml
# ponytail.config.yml
rules:
  no_direct_cognee_imports:
    description: "cognee must only be imported in core/providers/memory_provider.py"
    pattern: "import cognee"
    allowed_files: ["core/providers/memory_provider.py"]
    severity: error

  no_logic_in_routers:
    description: "Router functions should call a service or provider. No inline logic."
    files: ["api/routers/**/*.py"]
    max_function_lines: 20
    severity: warning

  phi_log_detection:
    description: "Detect potential PHI in log statements"
    pattern: "logger.(info|debug|warning|error).*symptom|diagnosis|medication|blood|glucose|pressure"
    severity: error

  family_id_required:
    description: "Repository methods must accept family_id as a parameter"
    files: ["core/repositories/**/*.py"]
    severity: warning

  no_raw_session_in_services:
    description: "Services must use repository classes, not direct db session"
    files: ["core/services/**/*.py"]
    pattern: "db.execute|db.query|db.add"
    severity: error

  no_direct_worker_calls:
    description: "Workers must not call each other directly. Use the Event Bus."
    files: ["core/workers/**/*.py"]
    pattern: "import.*workers\."
    severity: error

review_on:
  - pull_request
  - pre_commit

block_merge_on:
  - error
```

---

## Local Development Setup

Create a `docker-compose.yml` that starts:

1. `api` — FastAPI application on port 8000, hot-reload enabled, mounts `./` as volume
2. `worker` — ARQ worker process, same codebase as API
3. `postgres` — PostgreSQL 16, persistent volume, database `mantraone_dev`
4. `redis` — Redis 7, persistent volume (used for both cache and Event Bus Streams)
5. `cognee-setup` — One-shot container that configures Cognee to use the local PostgreSQL as its relational store and local Redis for caching

```
docker compose up
```

Should result in a fully working local environment with no additional configuration.

The `Dockerfile.worker` runs `python -m arq core.workers.worker_main.WorkerSettings` as its entrypoint.

All secrets in development come from a `.env.local` file (gitignored). In production they come from Google Secret Manager. The `config/settings.py` handles this switching automatically.

---

## Build Milestones

### Milestone 1 — Foundation (Week 1)
**Goal**: Running API with authentication, families, and members.

Agent tasks (run in parallel):
- **Database Agent**: Create all Alembic migrations for all tables above. Verify RLS policies. Seed test data.
- **Auth Agent**: Implement Firebase Auth middleware. GET /health, POST /v1/auth/verify, family/member CRUD endpoints.
- **Config Agent**: Set up `config/settings.py`, Docker Compose, `.env.local` template, pyproject.toml with all dependencies.
- **Event Bus Agent**: Implement `core/events/` — types, publisher, subscriber base class. Wire Redis Streams.

**Done when**: `docker compose up` starts cleanly. `POST /v1/families` creates a family. `GET /v1/families/me` returns it. All auth-protected routes reject unauthenticated requests. Events can be published and consumed.

### Milestone 2 — Health Data & Watcher Foundation (Week 2)
**Goal**: Health metrics, medications, check-ins, and the first 3 Watchers running.

Agent tasks (run in parallel):
- **Health Data Agent**: Implement health_metrics, medications, medication_logs endpoints and services.
- **Watcher Agent**: Implement BaseWatcher interface + Sleep, Medication, and Mood Watchers. ARQ worker setup.
- **Repository Agent**: Implement all repository classes with proper family_id scoping.

**Done when**: A health metric can be recorded. The Sleep Watcher runs and produces a WatcherSignal. The Medication Watcher detects a missed dose. Both publish events to the Event Bus.

### Milestone 3 — Memory Layer (Week 3)
**Goal**: Cognee integrated. Narratives being built and recalled.

Agent tasks:
- **Memory Agent**: Implement MemoryProvider, NarrativeBuilder worker (subscribing to Event Bus), and RetrievalService.
- **Narrative Agent**: Design and test narrative templates for each data type (checkin, health_metric, medication_log).
- **ADR Agent**: Write the first 7 ADRs in `docs/decisions/`.

**Done when**: A check-in response is submitted → `CHECKIN_SUBMITTED` event published → narrative built → stored in Cognee → `GET /v1/members/{id}/memory?q=sleep` returns relevant results.

### Milestone 4 — Coordinator & Escalation (Week 4)
**Goal**: The Coordinator picks one signal per day. Escalation Engine detects convergence.

Agent tasks:
- **Coordinator Agent**: Implement CoordinatorService, remaining 7 Watchers, ARQ scheduling.
- **Escalation Agent**: Implement EscalationEngine (Event Bus subscriber), ConsultationService, AI brief generation.

**Done when**: With fabricated test data showing multi-domain signal convergence, the Escalation Engine creates an EscalationEvent and generates a consultation AI brief. Ponytail review completed.

### Milestone 5 — Document Pipeline (Week 5)
**Goal**: PDF and image uploads processed, structured data extracted, ingested into Cognee.

Agent tasks:
- **Document Agent**: Implement the 4-step document processing pipeline end to end via Event Bus.

**Done when**: A lab report PDF is uploaded → processed through Event Bus pipeline → health_metrics created from results → memory ingested → `GET /v1/members/{id}/memory?q=lab results` returns the report context.

### Milestone 6 — Production Hardening (Week 6)
**Goal**: Security, observability, rate limiting, error handling production-ready.

Agent tasks:
- **Security Agent**: Rate limiting, audit logging on all PHI endpoints, input validation review, secret rotation setup.
- **Observability Agent**: OpenTelemetry traces on all operations, Cloud Monitoring dashboards, structured logging.
- **Performance Agent**: Database query analysis, N+1 detection, Redis caching. All Tier 1 endpoints must respond in under 300ms at p95.

**Done when**: Load test with 100 concurrent families shows p95 latency < 300ms for all Tier 1 endpoints. All PHI accesses appear in audit_logs.

### Milestone 7 — Scale Preparation (Week 7+)
- Watcher parallelization via Cloud Tasks (replace ARQ for high-volume)
- Cognee graph query optimization
- PostgreSQL read replica for timeline and memory queries
- Cloud Run autoscaling configuration
- Backup and disaster recovery procedures

---

## Engineering Principles (55)

1. Never call Cognee directly outside MemoryProvider.
2. Family is always the tenant. Every query scopes to family_id.
3. Silence is valid Coordinator output. Not every day needs a check-in.
4. Watchers do statistics. LLMs do language. Never reverse this.
5. Escalation requires convergence. Never act on a single data point.
6. PHI never appears in logs, URLs, error messages, or Redis keys.
7. Deviation from personal baseline matters more than deviation from population averages.
8. No business logic in routers. Routers call services. Full stop.
9. Every background worker is idempotent. Run it twice, same result.
10. Background tasks must not block the API response.
11. Every database operation filters by family_id. Trust nothing about what the caller provides.
12. PostgreSQL RLS is defense-in-depth, not the primary access control. Application enforces it too.
13. Encrypted fields are decrypted in the service layer, not the repository layer.
14. Documents are referenced by UUID. Original filenames never leave the storage layer.
15. Signed URLs expire in 15 minutes. Never create permanent public URLs for health documents.
16. Audit every PHI access. Every single one.
17. The Narrative Builder context window is the difference between facts and understanding.
18. A rich narrative with temporal context is worth 10 raw data points.
19. The Coordinator must enforce its own restraint in code, not just documentation.
20. AI brief for doctor consultations is generated before the consultation is booked, not after.
21. Never re-implement what Cognee already does. Extend it, wrap it, don't rewrite it.
22. Firebase Auth is the identity source of truth. Never store passwords.
23. Secrets come from Secret Manager in production. `.env.local` is for development only.
24. Every migration is reversible. Write the downgrade function even if it's a no-op.
25. Database schema changes and application changes deploy together via Blue-Green.
26. Cloud Run instances are stateless. All state lives in PostgreSQL, Redis, or Cognee.
27. Worker failures are logged, retried with exponential backoff, then dead-lettered.
28. Health baselines are recalculated weekly, not on every data point.
29. The Stress Watcher is the only Watcher that reads other Watchers' signals.
30. Family Care Watcher operates at family scope. All others operate at member scope.
31. Every API response that touches health data creates an audit log entry.
32. Repository classes never contain business logic. They contain queries.
33. Service classes never contain SQL. They call repositories.
34. Domain entities (in `core/domain/`) have zero infrastructure dependencies.
35. Pydantic v2 models are the contract between layers. Never return SQLAlchemy models from services.
36. Test the behavior, not the implementation. Mock infrastructure, not business logic.
37. Integration tests run against a real PostgreSQL and Redis, not mocks of them.
38. Cognee operations in tests use a test namespace, cleared between test runs.
39. A test that passes unreliably is worse than no test.
40. Ponytail runs on every commit. A Ponytail error blocks the CI pipeline.
41. OpenTelemetry traces start at the router and propagate through services and workers.
42. No user-facing error message ever reveals internal system state or stack traces.
43. Rate limiting is applied per Firebase UID, not per IP.
44. The AI brief for a doctor never contains fields the member hasn't explicitly shared.
45. Memory deletion is permanent and irreversible. Confirm explicitly before executing.
46. Soft deletes preserve data for GDPR response windows (30 days). Hard deletes happen after.
47. All time values are stored and compared in UTC. Display conversions happen at the edge.
48. The Coordinator decision for today is cached in Redis. Regenerate only if expired or invalidated.
49. Watcher signal severity levels are: low → medium → high → critical. Critical bypasses Coordinator.
50. This codebase is a living document. Architectural decisions must be recorded in `docs/decisions/`.
51. Workers communicate through the Event Bus, never through direct imports or calls.
52. If an endpoint exceeds 300ms, question the architecture — not just the query.
53. Every engineering decision should strengthen longitudinal family memory. If it doesn't, question it.
54. The product must feel like "someone keeping track" — never like an AI system.
55. We build WITH Cognee, not on top of it. Use its graph and memory correctly before adding more infrastructure.

---

## What Success Looks Like

When this backend is complete, the following scenario must work end to end:

1. A family signs up. Primary member onboarded with Firebase Auth.
2. Three family members added (parent, spouse, child).
3. Parent logs BP readings over 3 days via `POST /v1/health-metrics` → `HEALTH_METRIC_RECORDED` events flow through Event Bus.
4. Parent uploads a prescription PDF → document processed through Event Bus pipeline → medications created in DB → memory ingested.
5. Sleep Watcher detects declining sleep over 5 days → WatcherSignal created → `WATCHER_SIGNAL_EMITTED` event published.
6. Mood Watcher detects low mood check-ins → WatcherSignal created → event published.
7. Stress Watcher detects convergence of sleep + mood → composite stress signal created → event published.
8. Coordinator subscribes to Watcher events → selects stress domain as today's check-in → sends warm, contextual question referencing prior data.
9. Parent responds to check-in → `CHECKIN_SUBMITTED` event → NarrativeBuilder ingests rich narrative to Cognee.
10. `GET /v1/members/{id}/memory?q=stress and sleep patterns` returns semantically relevant context from Cognee.
11. Escalation Engine subscribes to Watcher events → detects 3-watcher convergence over 5 days → EscalationEvent created → GP consultation recommended.
12. AI brief generated → `GET /v1/consultations/{id}/brief` returns structured health context for the doctor.
13. `GET /v1/members/{id}/timeline` returns chronologically ordered health events from all sources.

This is not aspirational. This is the definition of done for the backend.

---

*MantraOne Engineering Constitution — v2. Every agent reads this before writing a single line of code.*
