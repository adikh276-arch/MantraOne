---
version: 1.0.0
owner: mantra_ai_team
status: production
created_at: 2026-06-27
description: Synthesizes a structured Doctor Brief.
---
# Clinical Handoff Brief

Generate a concise clinical brief intended for a physician.
Use the provided structured Digital Twin state.

Include:
- Chief Concern
- 14-Day Timeline of relevant changes
- Active Medications
- Supporting Evidence
- Missing Information
- Outstanding Questions
- Confidence Bounds
- Suggested Discussion Topics

Digital Twin Context:
{digital_twin}

Output MUST be valid JSON adhering strictly to the provided Pydantic schema. Do not include markdown formatting or prose.
