# 8. Event-Driven Architecture and Messaging Guarantees

Date: 2026-06-26

## Status
Accepted

## Context
MantraOne consists of independent layers (Watchers, Coordinator, Memory, Escalation). For loose coupling, these layers need to communicate without synchronous RPC calls or direct imports.

## Decision
We use a Redis Stream-based Event-Driven Architecture (EDA). 

## Guarantees Expected
- **At-Least-Once Delivery**: Redis Consumer Groups (`XREADGROUP`) ensure events are processed. Consumers must `XACK`.
- **Idempotency**: All event handlers must handle duplicate events safely via `idempotency_key`.
- **Event Sourcing**: Events append immutably to `mantraone:health_events`. They form a verifiable ledger.
