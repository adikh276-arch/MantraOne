---
version: 1.0.0
owner: mantra_ai_team
status: production
created_at: 2026-06-27
description: Generates domain-specific summarizations.
---
# Domain Summarization

Summarize the following health data according to the provided instructions.

Instructions:
{instructions}

Data:
{data}

Output MUST be valid JSON adhering strictly to the provided Pydantic schema. Do not include markdown formatting or prose.
