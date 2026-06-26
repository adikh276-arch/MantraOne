# MantraOne Engineering Constitution

## Build and Validation Source of Truth
- **Preferred Environment**: Native Python (`uv`)
- **Validation**: GitHub Actions builds production Docker images
- **Deployment**: Existing orchestration pipeline (via GitHub Actions Webhook)

*Docker Compose is optional and intended for contributors who have Docker installed locally.*

## User Journeys
Every feature must be traceable to a real user journey:
| User Journey | Backend Components |
|--------------|--------------------|
| Morning check-in | Check-in API -> Event Bus -> Watcher -> Coordinator -> Memory |
| Upload report | Upload API -> OCR -> Parser -> MemoryProvider -> Timeline |
| Doctor escalation | Watchers -> Coordinator -> Escalation -> Consultation Brief |
